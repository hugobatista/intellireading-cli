from io import BytesIO
import os
import zipfile

from lxml import etree
import pytest

from intellireading.client.__about_cli__ import __version__
from intellireading.client.metaguiding import (
    _ABOUT_PAGE_FILENAME,
    _ABOUT_PAGE_MANIFEST_ID,
    _DONATION_URL,
    _METAGUIDED_FLAG_FILENAME,
    _WEBSITE_URL,
    RegExBoldMetaguider,
    _EpubItemFile,
    _build_about_page,
    _find_opf_path,
    _inject_about_page,
    _is_apple_fixed_layout,
    _is_fixed_layout,
    _remove_about_page,
    _resolve_href_paths,
    metaguide_epub_stream,
)

_OPF_NS = "http://www.idpf.org/2007/opf"
_INPUT_EPUB = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")
_CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
_CHAPTER_XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter</title></head>
<body><p>Hello world</p></body>
</html>"""


def _simple_opf(
    version: str,
    *,
    metadata: str = "",
    manifest: str = "",
    spine: str = "",
    package_attributes: str = "",
) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="{_OPF_NS}" version="{version}" unique-identifier="uid"{package_attributes}>
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Test Book</dc:title>
    <dc:identifier id="uid">test-book</dc:identifier>
    <dc:language>en</dc:language>
    {metadata}
  </metadata>
  <manifest>
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
    {manifest}
  </manifest>
  <spine>
    <itemref idref="chapter"/>
    {spine}
  </spine>
</package>"""


def _build_epub(files: dict[str, str | bytes]) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as zip_file:
        zip_file.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    return stream.getvalue()


def _metaguide_input_epub(**kwargs: object) -> BytesIO:
    with open(_INPUT_EPUB, "rb") as input_file:
        return metaguide_epub_stream(BytesIO(input_file.read()), **kwargs)


def _opf_items(opf: str, extra_items: list[_EpubItemFile] | None = None) -> list[_EpubItemFile]:
    items = [
        _EpubItemFile("META-INF/container.xml", _CONTAINER_XML.encode()),
        _EpubItemFile("OEBPS/content.opf", opf.encode()),
    ]
    if extra_items:
        items.extend(extra_items)
    return items


def _manifest_items(root: etree._Element) -> list[etree._Element]:
    manifest = root.find(f"{{{_OPF_NS}}}manifest")
    assert manifest is not None
    return list(manifest)


def _spine_items(root: etree._Element) -> list[etree._Element]:
    spine = root.find(f"{{{_OPF_NS}}}spine")
    assert spine is not None
    return list(spine)


def _strip_bold_tags(html: str) -> str:
    return html.replace("<b>", "").replace("</b>", "")


def _assert_about_page_in_opf(opf_content: bytes, page_path: str) -> None:
    root = etree.fromstring(opf_content)
    about_items = [item for item in _manifest_items(root) if item.get("id") == _ABOUT_PAGE_MANIFEST_ID]
    assert len(about_items) == 1
    assert about_items[0].get("href") == _ABOUT_PAGE_FILENAME
    assert about_items[0].get("media-type") == "application/xhtml+xml"

    about_refs = [itemref for itemref in _spine_items(root) if itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID]
    assert len(about_refs) == 1
    assert _spine_items(root)[-1].get("idref") == _ABOUT_PAGE_MANIFEST_ID
    assert page_path.endswith(_ABOUT_PAGE_FILENAME)


def test_metaguide_epub_adds_about_page() -> None:
    output = _metaguide_input_epub()
    with zipfile.ZipFile(output) as zip_file:
        page_path = f"EPUB/{_ABOUT_PAGE_FILENAME}"
        assert page_path in zip_file.namelist()
        page = zip_file.read(page_path).decode()
        plain_page = _strip_bold_tags(page)
        assert "Thank you for using IntelliReading" in plain_page
        assert f"version {__version__}" in plain_page
        assert "<b>" in page
        assert f'<a href="{_DONATION_URL}"><b>{_DONATION_URL}</b></a>' in page
        assert f'<a href="{_WEBSITE_URL}"><b>{_WEBSITE_URL}</b></a>' in page
        assert "<b>htt</b>ps://" not in page
        _assert_about_page_in_opf(zip_file.read("EPUB/package.opf"), page_path)


def test_metaguide_epub_about_page_uses_fixation_level() -> None:
    level_1 = _metaguide_input_epub(fixation=1)
    level_5 = _metaguide_input_epub(fixation=5)

    with zipfile.ZipFile(level_1) as zip_file:
        page_level_1 = zip_file.read(f"EPUB/{_ABOUT_PAGE_FILENAME}").decode()
    with zipfile.ZipFile(level_5) as zip_file:
        page_level_5 = zip_file.read(f"EPUB/{_ABOUT_PAGE_FILENAME}").decode()

    assert page_level_1 != page_level_5


def test_metaguide_epub_removes_about_page() -> None:
    metaguided = _metaguide_input_epub()
    without_about_page = metaguide_epub_stream(metaguided, remove_metaguiding=True)

    with zipfile.ZipFile(without_about_page) as zip_file:
        page_path = f"EPUB/{_ABOUT_PAGE_FILENAME}"
        assert page_path not in zip_file.namelist()
        assert _METAGUIDED_FLAG_FILENAME not in zip_file.namelist()

        root = etree.fromstring(zip_file.read("EPUB/package.opf"))
        assert not any(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))
        assert not any(itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root))

        for filename in zip_file.namelist():
            if filename.endswith((".xhtml", ".html")):
                assert b"<b>" not in zip_file.read(filename)


def test_metaguide_epub_can_skip_about_page() -> None:
    output = _metaguide_input_epub(include_about_page=False)
    with zipfile.ZipFile(output) as zip_file:
        assert f"EPUB/{_ABOUT_PAGE_FILENAME}" not in zip_file.namelist()
        root = etree.fromstring(zip_file.read("EPUB/package.opf"))
        assert not any(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))
        assert _METAGUIDED_FLAG_FILENAME in zip_file.namelist()


def test_metaguide_epub_does_not_duplicate_about_page() -> None:
    first_output = _metaguide_input_epub()
    with zipfile.ZipFile(first_output) as zip_file:
        first_page = zip_file.read(f"EPUB/{_ABOUT_PAGE_FILENAME}")

    second_output = metaguide_epub_stream(BytesIO(first_output.getvalue()))

    with zipfile.ZipFile(second_output) as zip_file:
        assert zip_file.namelist().count(f"EPUB/{_ABOUT_PAGE_FILENAME}") == 1
        assert zip_file.read(f"EPUB/{_ABOUT_PAGE_FILENAME}") == first_page
        root = etree.fromstring(zip_file.read("EPUB/package.opf"))
        assert sum(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root)) == 1
        assert sum(itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root)) == 1


def test_metaguide_epub_remove_then_readd_has_single_about_page() -> None:
    first_output = _metaguide_input_epub()
    removed_output = metaguide_epub_stream(BytesIO(first_output.getvalue()), remove_metaguiding=True)
    readded_output = metaguide_epub_stream(BytesIO(removed_output.getvalue()))

    with zipfile.ZipFile(readded_output) as zip_file:
        assert zip_file.namelist().count(f"EPUB/{_ABOUT_PAGE_FILENAME}") == 1
        page = zip_file.read(f"EPUB/{_ABOUT_PAGE_FILENAME}").decode()
        assert "<b>" in page
        assert f'<a href="{_DONATION_URL}"><b>{_DONATION_URL}</b></a>' in page
        root = etree.fromstring(zip_file.read("EPUB/package.opf"))
        assert sum(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root)) == 1
        assert sum(itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root)) == 1


def test_metaguide_epub_does_not_change_already_metaguided_epub() -> None:
    epub = _build_epub(
        {
            "META-INF/container.xml": _CONTAINER_XML,
            "OEBPS/content.opf": _simple_opf("3.0"),
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
            _METAGUIDED_FLAG_FILENAME: b"version: 2.1.2",
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        assert f"OEBPS/{_ABOUT_PAGE_FILENAME}" not in zip_file.namelist()
        assert zip_file.read("OEBPS/chapter.xhtml") == _CHAPTER_XHTML
        assert _METAGUIDED_FLAG_FILENAME in zip_file.namelist()


@pytest.mark.parametrize(
    ("version", "expected_doctype", "expected_meta", "unexpected_meta"),
    [
        ("2.0", "XHTML 1.1", 'http-equiv="Content-Type"', '<meta charset="utf-8"/>'),
        ("3.0", "<!DOCTYPE html>", '<meta charset="utf-8"/>', 'http-equiv="Content-Type"'),
    ],
)
def test_build_about_page_uses_version_compatible_markup(
    version: str,
    expected_doctype: str,
    expected_meta: str,
    unexpected_meta: str,
) -> None:
    page = _build_about_page(version).decode()

    assert expected_doctype in page
    assert expected_meta in page
    assert unexpected_meta not in page
    assert f"version {__version__}" in page


def test_build_about_page_escapes_version() -> None:
    page = _build_about_page("3.0", tool_version='3.0"><script>').decode()

    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_build_about_page_has_visible_urls() -> None:
    page = _build_about_page("3.0").decode()

    assert f'<a href="{_DONATION_URL}"><b>{_DONATION_URL}</b></a>' in page
    assert f'<a href="{_WEBSITE_URL}"><b>{_WEBSITE_URL}</b></a>' in page


def test_metaguide_epub_adds_epub2_compatible_about_page() -> None:
    epub = _build_epub(
        {
            "META-INF/container.xml": _CONTAINER_XML,
            "OEBPS/content.opf": _simple_opf("2.0"),
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        page_path = f"OEBPS/{_ABOUT_PAGE_FILENAME}"
        page = zip_file.read(page_path).decode()
        assert "XHTML 1.1" in page
        assert 'http-equiv="Content-Type"' in page
        assert '<meta charset="utf-8"/>' not in page
        assert "<b>" in page
        assert f'<a href="{_DONATION_URL}"><b>{_DONATION_URL}</b></a>' in page
        _assert_about_page_in_opf(zip_file.read("OEBPS/content.opf"), page_path)


def test_metaguide_epub_skips_about_page_for_fixed_layout() -> None:
    epub = _build_epub(
        {
            "META-INF/container.xml": _CONTAINER_XML,
            "OEBPS/content.opf": _simple_opf("3.0", metadata='<meta property="rendition:layout">pre-paginated</meta>'),
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        assert f"OEBPS/{_ABOUT_PAGE_FILENAME}" not in zip_file.namelist()
        assert _METAGUIDED_FLAG_FILENAME in zip_file.namelist()


def test_metaguide_epub_skips_about_page_for_apple_fixed_layout() -> None:
    epub = _build_epub(
        {
            "META-INF/container.xml": _CONTAINER_XML,
            "META-INF/com.apple.ibooks.display-options.xml": _apple_display_options("true"),
            "OEBPS/content.opf": _simple_opf("2.0"),
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        assert f"OEBPS/{_ABOUT_PAGE_FILENAME}" not in zip_file.namelist()
        assert _METAGUIDED_FLAG_FILENAME in zip_file.namelist()


def test_metaguide_epub_survives_invalid_opf() -> None:
    epub = _build_epub(
        {
            "META-INF/container.xml": _CONTAINER_XML,
            "OEBPS/content.opf": "<package",
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        assert f"OEBPS/{_ABOUT_PAGE_FILENAME}" not in zip_file.namelist()
        assert _METAGUIDED_FLAG_FILENAME in zip_file.namelist()


def test_metaguide_epub_finds_single_opf_without_container() -> None:
    epub = _build_epub(
        {
            "OEBPS/content.opf": _simple_opf("3.0"),
            "OEBPS/chapter.xhtml": _CHAPTER_XHTML,
        }
    )

    output = metaguide_epub_stream(BytesIO(epub))

    with zipfile.ZipFile(output) as zip_file:
        page_path = f"OEBPS/{_ABOUT_PAGE_FILENAME}"
        assert page_path in zip_file.namelist()
        _assert_about_page_in_opf(zip_file.read("OEBPS/content.opf"), page_path)


def test_find_opf_path_falls_back_when_container_is_invalid() -> None:
    items = [
        _EpubItemFile("META-INF/container.xml", b"<container"),
        _EpubItemFile("OEBPS/content.opf", b"<package/>"),
    ]

    assert _find_opf_path(items) == "OEBPS/content.opf"


def test_find_opf_path_falls_back_when_container_points_to_missing_opf() -> None:
    container = _CONTAINER_XML.replace("OEBPS/content.opf", "OEBPS/missing.opf")
    items = [
        _EpubItemFile("META-INF/container.xml", container.encode()),
        _EpubItemFile("OEBPS/content.opf", b"<package/>"),
    ]

    assert _find_opf_path(items) == "OEBPS/content.opf"


def test_find_opf_path_returns_none_for_multiple_opf_without_container() -> None:
    items = [_EpubItemFile("one.opf", b"<package/>"), _EpubItemFile("two.opf", b"<package/>")]

    assert _find_opf_path(items) is None


@pytest.mark.parametrize(
    ("metadata", "spine"),
    [
        ('<meta property="rendition:layout">pre-paginated</meta>', ""),
        ('<meta name="fixed-layout" content="true"/>', ""),
        ("", '<itemref idref="chapter" properties="rendition:layout-pre-paginated"/>'),
    ],
)
def test_is_fixed_layout_detects_common_markers(metadata: str, spine: str) -> None:
    root = etree.fromstring(
        f'<package xmlns="{_OPF_NS}"><metadata>{metadata}</metadata><manifest/><spine>{spine}</spine></package>'
    )

    assert _is_fixed_layout(root)


def test_is_fixed_layout_returns_false_for_reflowable() -> None:
    root = etree.fromstring(f'<package xmlns="{_OPF_NS}"><metadata/><manifest/><spine/></package>')

    assert not _is_fixed_layout(root)


def _apple_display_options(fixed_layout: str) -> bytes:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<display_options>
  <platform name="*">
    <option name="fixed-layout">{fixed_layout}</option>
  </platform>
</display_options>""".encode()


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (_apple_display_options("true"), True),
        (_apple_display_options("false"), False),
        (b"<display_options", False),
    ],
)
def test_is_apple_fixed_layout(content: bytes, expected: bool) -> None:  # noqa: FBT001
    items = [_EpubItemFile("META-INF/com.apple.ibooks.display-options.xml", content)]

    assert _is_apple_fixed_layout(items) is expected


def test_is_apple_fixed_layout_returns_false_without_options_file() -> None:
    assert not _is_apple_fixed_layout([_EpubItemFile("META-INF/container.xml", _CONTAINER_XML.encode())])


@pytest.mark.parametrize(
    ("opf_dir", "href", "expected"),
    [
        ("OEBPS", "intellireading-about.xhtml", {"OEBPS/intellireading-about.xhtml"}),
        ("OEBPS", "intellireading-about.xhtml#top", {"OEBPS/intellireading-about.xhtml"}),
        ("OEBPS", "intellireading-about.xhtml?version=1", {"OEBPS/intellireading-about.xhtml"}),
        ("OEBPS", "/intellireading-about.xhtml", {"OEBPS/intellireading-about.xhtml"}),
        ("OEBPS", "", set()),
        ("", "intellireading-about.xhtml", {"intellireading-about.xhtml"}),
    ],
)
def test_resolve_href_paths(opf_dir: str, href: str, expected: set[str]) -> None:
    assert _resolve_href_paths(opf_dir, href) == expected


def test_inject_about_page_skips_when_page_file_already_exists() -> None:
    items = _opf_items(
        _simple_opf("3.0"),
        [_EpubItemFile(f"OEBPS/{_ABOUT_PAGE_FILENAME}", b"existing page")],
    )

    assert not _inject_about_page(items, RegExBoldMetaguider())


def test_inject_about_page_skips_when_manifest_already_has_about_item() -> None:
    opf = _simple_opf(
        "3.0", manifest='<item id="intellireading-about" href="other.xhtml" media-type="application/xhtml+xml"/>'
    )
    items = _opf_items(opf)

    assert not _inject_about_page(items, RegExBoldMetaguider())


def test_inject_about_page_skips_when_spine_has_about_itemref_without_manifest_item() -> None:
    opf = _simple_opf("3.0", spine=f'<itemref idref="{_ABOUT_PAGE_MANIFEST_ID}"/>')
    items = _opf_items(opf)

    assert not _inject_about_page(items, RegExBoldMetaguider())

    root = etree.fromstring(next(item for item in items if item.filename == "OEBPS/content.opf").content)
    assert not any(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))
    assert sum(itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root)) == 1


def test_inject_about_page_skips_case_variant_page_file() -> None:
    items = _opf_items(
        _simple_opf("3.0"),
        [_EpubItemFile("OEBPS/IntelliReading-About.xhtml", b"existing page")],
    )

    assert not _inject_about_page(items, RegExBoldMetaguider())
    assert not any(item.filename == f"OEBPS/{_ABOUT_PAGE_FILENAME}" for item in items)


def test_inject_about_page_skips_case_variant_manifest_item() -> None:
    opf = _simple_opf(
        "3.0",
        manifest='<item id="IntelliReading-About" href="IntelliReading-About.xhtml" '
        'media-type="application/xhtml+xml"/>',
    )
    items = _opf_items(opf)

    assert not _inject_about_page(items, RegExBoldMetaguider())

    root = etree.fromstring(next(item for item in items if item.filename == "OEBPS/content.opf").content)
    assert not any(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))


def test_inject_about_page_skips_when_xml_base_is_used() -> None:
    opf = _simple_opf("3.0", package_attributes=' xml:base="OEBPS"')
    items = _opf_items(opf)

    assert not _inject_about_page(items, RegExBoldMetaguider())


def test_inject_about_page_skips_without_manifest_or_spine() -> None:
    opf = f'<package xmlns="{_OPF_NS}" version="3.0"><metadata/></package>'
    items = _opf_items(opf)

    assert not _inject_about_page(items, RegExBoldMetaguider())


def test_inject_about_page_handles_opf_without_namespace() -> None:
    opf = _simple_opf("3.0").replace(f' xmlns="{_OPF_NS}"', "")
    items = _opf_items(opf)

    assert _inject_about_page(items, RegExBoldMetaguider())
    opf_item = next(item for item in items if item.filename == "OEBPS/content.opf")
    root = etree.fromstring(opf_item.content)
    assert root.find("manifest/item[@id='intellireading-about']") is not None


def test_inject_about_page_preserves_opf_doctype() -> None:
    opf = _simple_opf("3.0").replace("?>\n<package", "?>\n<!DOCTYPE package>\n<package")
    items = _opf_items(opf)

    assert _inject_about_page(items, RegExBoldMetaguider())
    opf_item = next(item for item in items if item.filename == "OEBPS/content.opf")
    assert b"<!DOCTYPE package>" in opf_item.content


def test_remove_about_page_returns_false_when_no_page_exists() -> None:
    items = _opf_items(_simple_opf("3.0"))

    assert not _remove_about_page(items)


def test_remove_about_page_returns_false_without_opf() -> None:
    items = [_EpubItemFile("OEBPS/chapter.xhtml", _CHAPTER_XHTML)]

    assert not _remove_about_page(items)


def test_remove_about_page_returns_false_for_invalid_opf() -> None:
    items = [
        _EpubItemFile("META-INF/container.xml", _CONTAINER_XML),
        _EpubItemFile("OEBPS/content.opf", b"<package"),
    ]

    assert not _remove_about_page(items)


def test_remove_about_page_removes_orphan_page_file() -> None:
    items = _opf_items(
        _simple_opf("3.0"),
        [_EpubItemFile(f"OEBPS/{_ABOUT_PAGE_FILENAME}", b"orphan page")],
    )

    assert _remove_about_page(items)
    assert not any(item.filename == f"OEBPS/{_ABOUT_PAGE_FILENAME}" for item in items)


def test_remove_about_page_removes_opf_entries_when_page_file_is_missing() -> None:
    opf = _simple_opf(
        "3.0",
        manifest=f'<item id="{_ABOUT_PAGE_MANIFEST_ID}" href="{_ABOUT_PAGE_FILENAME}" '
        'media-type="application/xhtml+xml"/>',
        spine=f'<itemref idref="{_ABOUT_PAGE_MANIFEST_ID}"/>',
    )
    items = _opf_items(opf)

    assert _remove_about_page(items)
    root = etree.fromstring(next(item for item in items if item.filename == "OEBPS/content.opf").content)
    assert not any(item.get("id") == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))
    assert not any(itemref.get("idref") == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root))


def test_remove_about_page_removes_case_variant_entries() -> None:
    opf = _simple_opf(
        "3.0",
        manifest='<item id="IntelliReading-About" href="IntelliReading-About.xhtml" '
        'media-type="application/xhtml+xml"/>',
        spine='<itemref idref="IntelliReading-About"/>',
    )
    items = _opf_items(opf, [_EpubItemFile("OEBPS/IntelliReading-About.xhtml", b"existing page")])

    assert _remove_about_page(items)

    root = etree.fromstring(next(item for item in items if item.filename == "OEBPS/content.opf").content)
    assert not any((item.get("id") or "").lower() == _ABOUT_PAGE_MANIFEST_ID for item in _manifest_items(root))
    assert not any((itemref.get("idref") or "").lower() == _ABOUT_PAGE_MANIFEST_ID for itemref in _spine_items(root))
    assert not any(item.filename and item.filename.lower().endswith(_ABOUT_PAGE_FILENAME) for item in items)


def test_about_page_file_is_not_metaguided() -> None:
    item = _EpubItemFile(f"OEBPS/{_ABOUT_PAGE_FILENAME}", _CHAPTER_XHTML)
    original_content = item.content

    item.metaguide(RegExBoldMetaguider())

    assert item.content == original_content
