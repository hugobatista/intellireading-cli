import os
import re
import zipfile
from io import BytesIO

import pytest

from intellireading.client import metaguide_dir, metaguide_epub_stream
from intellireading.client.metaguiding import DEFAULT_FIXATION, FIXATION_LEVELS, RegExBoldMetaguider

_TRUNCATED_XML_HEADER = b'<?xml version="1.0" encoding="utf-8"'
_TRUNCATED_HEADER_WITH_BODY = _TRUNCATED_XML_HEADER + b"<html><body><p>hello world</p></body></html>"


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
