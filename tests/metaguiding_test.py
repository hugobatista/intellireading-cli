import os
import re
import zipfile
from io import BytesIO

import pytest
from lxml import etree

from intellireading.client import metaguide_dir, metaguide_epub_stream
from intellireading.client.metaguiding import DEFAULT_FIXATION, FIXATION_LEVELS, RegExBoldMetaguider

_TRUNCATED_XML_HEADER = b'<?xml version="1.0" encoding="utf-8"'
_TRUNCATED_HEADER_WITH_BODY = _TRUNCATED_XML_HEADER + b"<html><body><p>hello world</p></body></html>"

_NON_PROSE_XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>t</title></head>
<body>
<style>p { font-size: 200%; margin: 3em; }</style>
<script>var x = "plain text";</script>
<pre>  code   sample  </pre>
<code>inline code sample</code>
<!-- comment with some prose -->
<p>Normal text here.</p>
</body>
</html>
"""

_EXPECTED_NON_PROSE_XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>t</title></head>
<body>
<style>p { font-size: 200%; margin: 3em; }</style>
<script>var x = "plain text";</script>
<pre>  code   sample  </pre>
<code>inline code sample</code>
<!-- comment with some prose -->
<p><b>Nor</b>mal <b>te</b>xt <b>he</b>re.</p>
</body>
</html>
"""

_SVG_CDATA_XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body>
<svg xmlns="http://www.w3.org/2000/svg"><![CDATA[<style>.x { fill: red; }</style>]]>\
<text x="0">svg text sample</text><tspan>span sample</tspan></svg>
<p>Normal text here.</p>
</body></html>
"""


@pytest.mark.parametrize(
    "document",
    [
        _TRUNCATED_XML_HEADER,
        _TRUNCATED_HEADER_WITH_BODY,
        b'<?xml version="1.0"',
    ],
)
def test_get_encoding_using_xml_header_returns_none_for_truncated_header(document: bytes) -> None:
    metaguider = RegExBoldMetaguider()

    assert metaguider._get_encoding_using_xml_header(document) is None


def test_get_encoding_falls_back_for_truncated_xml_header() -> None:
    metaguider = RegExBoldMetaguider(fallback_encoding="iso-8859-1")

    assert metaguider._get_encoding(_TRUNCATED_HEADER_WITH_BODY) == "iso-8859-1"


def test_metaguide_xhtml_document_with_truncated_xml_header_does_not_raise() -> None:
    metaguider = RegExBoldMetaguider()

    result = metaguider.metaguide_xhtml_document(_TRUNCATED_HEADER_WITH_BODY)

    assert b"<b>" in result


def test_metaguide_xhtml_document_preserves_non_prose_regions() -> None:
    result = RegExBoldMetaguider().metaguide_xhtml_document(_NON_PROSE_XHTML)

    assert result == _EXPECTED_NON_PROSE_XHTML


def test_metaguide_xhtml_document_preserves_cdata_and_svg_text() -> None:
    result = RegExBoldMetaguider().metaguide_xhtml_document(_SVG_CDATA_XHTML)

    assert b"<![CDATA[<style>.x { fill: red; }</style>]]>" in result
    assert b'<text x="0">svg text sample</text>' in result
    assert b"<tspan>span sample</tspan>" in result
    assert b"<b>Nor</b>mal <b>te</b>xt <b>he</b>re." in result
    assert etree.fromstring(result) is not None


def test_metaguide_xhtml_document_preserves_comments_containing_tags() -> None:
    document = b"<html><body><!-- <style>.a{}</style> keep --><p>prose here</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<!-- <style>.a{}</style> keep -->" in result
    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_preserves_prefixed_svg_elements() -> None:
    document = (
        b'<html><body><svg:svg xmlns:svg="http://www.w3.org/2000/svg">'
        b"<svg:style>.a{fill:red}</svg:style><svg:script>var x = 1;</svg:script>"
        b'<svg:text x="0">svg text sample</svg:text><svg:tspan>span sample</svg:tspan>'
        b"</svg:svg><p>prose here</p></body></html>"
    )

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<svg:style>.a{fill:red}</svg:style>" in result
    assert b"<svg:script>var x = 1;</svg:script>" in result
    assert b'<svg:text x="0">svg text sample</svg:text>' in result
    assert b"<svg:tspan>span sample</svg:tspan>" in result
    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_preserves_uppercase_prefixed_elements() -> None:
    document = b"<html><body><SVG:text>svg sample</SVG:text><p>prose here</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<SVG:text>svg sample</SVG:text>" in result
    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_preserves_uppercase_and_attribute_regions() -> None:
    document = (
        b'<html><body><STYLE type="text/css">a{color:red}</STYLE>'
        b'<SCRIPT src="book.js"></SCRIPT><PRE class="code">keep me</PRE>'
        b"<p>prose here</p></body></html>"
    )

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b'<STYLE type="text/css">a{color:red}</STYLE>' in result
    assert b'<SCRIPT src="book.js"></SCRIPT>' in result
    assert b'<PRE class="code">keep me</PRE>' in result
    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_preserves_regions_with_attributes_containing_gt() -> None:
    document = (
        b'<html><body><pre data-x="a>b">keep me</pre><style data-y="c>d">.a{}</style><p>prose here</p></body></html>'
    )

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b'<pre data-x="a>b">keep me</pre>' in result
    assert b'<style data-y="c>d">.a{}</style>' in result
    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_preserves_empty_non_prose_regions() -> None:
    document = b"<html><body><style></style><pre></pre><code></code><!-- --><p>prose here</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert result == (
        b"<html><body><style></style><pre></pre><code></code><!-- --><p><b>pro</b>se <b>he</b>re</p></body></html>"
    )


def test_metaguide_xhtml_document_does_not_swallow_prose_after_self_closing_script() -> None:
    document = b'<html><body><script src="a.js"/><p>prose here</p><script>var x = 1;</script></body></html>'

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b'<script src="a.js"/>' in result
    assert b"<b>pro</b>se <b>he</b>re" in result
    assert b"<script>var x = 1;</script>" in result


def test_metaguide_xhtml_document_does_not_swallow_prose_after_unterminated_region() -> None:
    document = b"<html><body><style>a { color: red }<p>prose here</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<b>pro</b>se <b>he</b>re" in result


def test_metaguide_xhtml_document_restores_adjacent_non_prose_regions() -> None:
    document = (
        b"<html><body><style>.a{}</style><script>var b = 1;</script>"
        b"<pre>c c c</pre><code>d d d</code><!-- e e e -->"
        b"<![CDATA[f f f]]><p>prose here</p></body></html>"
    )

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    for region in (
        b"<style>.a{}</style>",
        b"<script>var b = 1;</script>",
        b"<pre>c c c</pre>",
        b"<code>d d d</code>",
        b"<!-- e e e -->",
        b"<![CDATA[f f f]]>",
    ):
        assert region in result
    assert b"<b>pro</b>se <b>he</b>re" in result


@pytest.mark.parametrize(
    "document",
    [
        b"<html><body><style>a{}</style>bare text here<p>wrapped text here</p></body></html>",
        b"<html><body><pre>keep</pre>bare text here<p>wrapped text here</p></body></html>",
        b"<html><body><!-- note -->bare text here<p>wrapped text here</p></body></html>",
        b"<html><body><![CDATA[a > b]]>bare text here<p>wrapped text here</p></body></html>",
    ],
)
def test_metaguide_xhtml_document_bolds_prose_after_leading_non_prose_region(document: bytes) -> None:
    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<b>ba</b>re <b>te</b>xt <b>he</b>re" in result
    assert b"<b>wrap</b>ped <b>te</b>xt <b>he</b>re" in result


def test_metaguide_xhtml_document_bolds_prose_after_inline_code_inside_bold() -> None:
    document = b"<html><body><p><b><code>x</code>bolded text</b></p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<b><code>x</code><b>bol</b>ded <b>te</b>xt</b>" in result


def test_metaguide_xhtml_document_bolds_prose_around_inline_code() -> None:
    document = b"<html><body><p>Use the <code>--flag</code> option here.</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"<code>--flag</code>" in result
    assert b"<b>U</b>se <b>t</b>he " in result
    assert b" <b>opt</b>ion <b>he</b>re." in result


def test_metaguide_xhtml_document_preserves_entities_and_existing_bold_tags() -> None:
    document = b"<html><body><p>Tom &amp; Jerry <b>already</b> bold &lt;tag&gt;</p></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert result == (
        b"<html><body><p><b>T</b>om &amp; <b>Jer</b>ry <b>already</b> <b>bo</b>ld &lt;<b>t</b>ag&gt;</p></body></html>"
    )


def test_metaguide_xhtml_document_preserves_non_prose_regions_in_non_utf8_document() -> None:
    document = (
        '<?xml version="1.0" encoding="iso-8859-1"?>'
        '<html><body><style>p::after { content: "café"; }</style>'
        '<script>var message = "olá";</script><p>Normal text here.</p></body></html>'
    ).encode("iso-8859-1")

    result = RegExBoldMetaguider().metaguide_xhtml_document(document).decode("iso-8859-1")

    assert '<style>p::after { content: "café"; }</style>' in result
    assert '<script>var message = "olá";</script>' in result
    assert "<b>Nor</b>mal <b>te</b>xt <b>he</b>re." in result


def test_metaguide_xhtml_document_preserves_non_prose_regions_with_fallback_encoding() -> None:
    document = (
        '<html><body><style>p::after { content: "café"; }</style>'
        '<script>var message = "olá";</script><p>Normal text here.</p></body></html>'
    ).encode("iso-8859-1")

    result = RegExBoldMetaguider(fallback_encoding="iso-8859-1").metaguide_xhtml_document(document)
    decoded = result.decode("iso-8859-1")

    assert '<style>p::after { content: "café"; }</style>' in decoded
    assert '<script>var message = "olá";</script>' in decoded
    assert "<b>Nor</b>mal <b>te</b>xt <b>he</b>re." in decoded


def test_metaguide_xhtml_document_tolerates_internal_sentinel_in_body() -> None:
    document = b"<html><body><p>Normal \x00\x01 text</p><style>a{color:red}</style></body></html>"

    result = RegExBoldMetaguider().metaguide_xhtml_document(document)

    assert b"\x00\x01 <b>te</b>xt" in result
    assert b"<b>Nor</b>mal" in result


@pytest.mark.parametrize(
    ("body", "contents"),
    [
        ("\x00\x01", []),
        ("no sentinel", ["region"]),
    ],
)
def test_restore_non_prose_regions_rejects_sentinel_count_mismatch(body: str, contents: list[str]) -> None:
    metaguider = RegExBoldMetaguider()

    with pytest.raises(RuntimeError, match="non-prose sentinels"):
        metaguider._restore_non_prose_regions(body, contents)


def test_remove_metaguiding_preserves_literal_bold_tags_in_script() -> None:
    document = b'<html><body><script>var x = "<b>hello</b>";</script><p>Normal text here.</p></body></html>'
    metaguider = RegExBoldMetaguider()

    metaguided = metaguider.metaguide_xhtml_document(document)

    assert b'<script>var x = "<b>hello</b>";</script>' in metaguided
    assert metaguider.metaguide_xhtml_document(metaguided, remove_metaguiding=True) == document


def test_remove_metaguiding_restores_metaguided_non_prose_document() -> None:
    metaguider = RegExBoldMetaguider()
    metaguided = metaguider.metaguide_xhtml_document(_NON_PROSE_XHTML)

    assert metaguider.metaguide_xhtml_document(metaguided, remove_metaguiding=True) == _NON_PROSE_XHTML


def test_remove_metaguiding_repairs_legacy_bold_tags_in_non_prose_regions() -> None:
    document = (
        b"<html><body><style><b>p</b> { <b>fo</b>nt-<b>si</b>ze: 200%; }</style>"
        b"<script><b>v</b>ar <b>x</b> = 1;</script><p><b>Nor</b>mal text</p></body></html>"
    )

    result = RegExBoldMetaguider().metaguide_xhtml_document(document, remove_metaguiding=True)

    assert b"<style>p { font-size: 200%; }</style>" in result
    assert b"<script>var x = 1;</script>" in result
    assert b"<p>Normal text</p>" in result


@pytest.mark.parametrize(
    ("document", "expected"),
    [
        (b'<?xml version="1.0" encoding="utf-8"?><html/>', "utf-8"),
        (b"<?xml version='1.0' encoding='ISO-8859-1'?><html/>", "ISO-8859-1"),
        (b'<?xml version="1.0"?><html/>', None),
        (b"<html/>", None),
    ],
)
def test_get_encoding_using_xml_header(document: bytes, expected: str | None) -> None:
    metaguider = RegExBoldMetaguider()

    assert metaguider._get_encoding_using_xml_header(document) == expected


@pytest.mark.parametrize(
    ("fixation", "word", "expected"),
    [
        (1, "a", "<b>a</b>"),
        (5, "a", "<b>a</b>"),
        (1, "ab", "<b>a</b>b"),
        (5, "ab", "<b>a</b>b"),
        (3, "abc", "<b>a</b>bc"),
        (4, "abc", "<b>ab</b>c"),
        (5, "abc", "<b>ab</b>c"),
        (1, "abcd", "<b>ab</b>cd"),
        (3, "abcd", "<b>ab</b>cd"),
        (4, "abcd", "<b>abc</b>d"),
        (1, "abcde", "<b>ab</b>cde"),
        (2, "abcde", "<b>ab</b>cde"),
        (3, "abcde", "<b>abc</b>de"),
        (4, "abcde", "<b>abc</b>de"),
        (5, "abcde", "<b>abcd</b>e"),
        (1, "abcdefghij", "<b>abc</b>defghij"),
        (2, "abcdefghij", "<b>abcd</b>efghij"),
        (3, "abcdefghij", "<b>abcde</b>fghij"),
        (4, "abcdefghij", "<b>abcdef</b>ghij"),
        (5, "abcdefghij", "<b>abcdefg</b>hij"),
    ],
)
def test_bold_word_uses_fixation_level(fixation: int, word: str, expected: str) -> None:
    metaguider = RegExBoldMetaguider(fixation=fixation)

    assert metaguider._bold_word(word) == expected


@pytest.mark.parametrize("word", ["a", "in", "the", "word", "reading", "metaguiding"])
def test_default_fixation_matches_level_three(word: str) -> None:
    assert DEFAULT_FIXATION == 3
    assert RegExBoldMetaguider()._bold_word(word) == RegExBoldMetaguider(fixation=3)._bold_word(word)


def test_default_fixation_keeps_historical_bold_splits() -> None:
    metaguider = RegExBoldMetaguider()

    assert metaguider._bold_word("the") == "<b>t</b>he"
    assert metaguider._bold_word("word") == "<b>wo</b>rd"
    assert metaguider._bold_word("reading") == "<b>read</b>ing"
    assert metaguider._bold_word("metaguiding") == "<b>metagu</b>iding"


@pytest.mark.parametrize("fixation", [0, 6, -1])
def test_invalid_fixation_level_raises(fixation: int) -> None:
    with pytest.raises(ValueError, match="Invalid fixation level"):
        RegExBoldMetaguider(fixation=fixation)


@pytest.mark.parametrize("fixation", [True, 2.0, "3", [3]])
def test_invalid_fixation_type_raises(fixation: object) -> None:
    with pytest.raises(ValueError, match="Invalid fixation level"):
        RegExBoldMetaguider(fixation=fixation)  # type: ignore[arg-type]


def test_fixation_levels_are_one_to_five() -> None:
    assert FIXATION_LEVELS == (1, 2, 3, 4, 5)
    assert DEFAULT_FIXATION in FIXATION_LEVELS


_INPUT_EPUB = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")
_CHAPTER_PATH = "EPUB/xhtml/basic_tests.xhtml"


def _chapter_bold_lengths(fixation: int) -> list[int]:
    with open(_INPUT_EPUB, "rb") as input_file:
        output = metaguide_epub_stream(BytesIO(input_file.read()), fixation=fixation, include_about_page=False)

    with zipfile.ZipFile(output) as zip_file:
        content = zip_file.read(_CHAPTER_PATH).decode("utf-8")

    return [len(bold) for bold in re.findall(r"<b>(.*?)</b>", content, re.DOTALL)]


def test_metaguide_epub_stream_uses_fixation_in_chapters() -> None:
    level_1 = _chapter_bold_lengths(1)
    level_5 = _chapter_bold_lengths(5)

    assert level_1
    assert len(level_1) == len(level_5)
    assert sum(level_1) < sum(level_5)


def test_metaguide_dir_rejects_invalid_fixation(tmp_path) -> None:
    output_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="Invalid fixation level"):
        metaguide_dir(os.path.dirname(_INPUT_EPUB), str(output_dir), fixation=0)

    assert not output_dir.exists()
