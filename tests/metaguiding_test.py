import pytest

from intellireading.client.metaguiding import RegExBoldMetaguider

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
