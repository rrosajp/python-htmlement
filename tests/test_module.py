#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 2 compatibility
import xml.etree.ElementTree as Etree
import htmlement
import examples
import tempfile
import pytest
import io
import os


def quick_parsehtml(html, encoding=""):
    obj = htmlement.HTMLement(encoding=encoding)
    obj.feed(html)
    root = obj.close()
    assert Etree.iselement(root)
    return root


def quick_parse_filter(html, tag, attrs=None, encoding=""):
    obj = htmlement.HTMLement(tag, attrs, encoding=encoding)
    obj.feed(html)
    return obj.close()


def test_initialization():
    # Check that the parser even starts
    obj = htmlement.HTMLement()
    assert isinstance(obj, htmlement.HTMLement)


# ############################# HTML Test ############################## #


def test_basic_tree():
    # Check that I can parse a simple tree
    html = "<html><body></body></html>"
    root = quick_parsehtml(html)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_basic_partial():
    # Check that I can parse a simple tree segment at a time
    html = "<html><body></body></html>"
    obj = htmlement.HTMLement()
    obj.feed(html[:9])
    obj.feed(html[9:])
    root = obj.close()
    assert Etree.iselement(root)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_nohtml_tree():
    # Check that the missing html starting tag is created
    html = "<body></body>"
    root = quick_parsehtml(html)
    assert root.tag == "html"
    assert root[0].tag == "body"
    assert Etree.tostring(root, method="html") == b'<html><body></body></html>'


def test_text():
    html = "<html><body>text</body></html>"
    root = quick_parsehtml(html)
    assert root.tag == "html"
    assert root[0].tag == "body"
    assert root[0].attrib == {}
    assert root[0].text == "text"


def test_attrib():
    html = "<html><body test='yes'>text</body></html>"
    root = quick_parsehtml(html)
    assert root[0].attrib == {"test": "yes"}


def test_tail():
    html = "<html><body test='yes'><p>text</p>tail</body></html>"
    root = quick_parsehtml(html)
    assert root[0][0].tail == "tail"


def test_self_closing_normal():
    html = "<html><check test='self closing'/></html>"
    root = quick_parsehtml(html)
    assert root[0].attrib.get("test") == "self closing"


def test_self_closing_void():
    html = "<html><img src='http://myimages.com/myimage.jpg'/></html>"
    root = quick_parsehtml(html)
    assert root[0].tag == "img"
    assert root[0].attrib.get("src") == "http://myimages.com/myimage.jpg"


def test_open_void():
    html = "<html><img src='http://myimages.com/myimage.jpg'></html>"
    root = quick_parsehtml(html)
    assert root[0].tag == "img"
    assert root[0].attrib.get("src") == "http://myimages.com/myimage.jpg"


def test_comment():
    html = "<html><body><!--This is a comment.--><p>This is a paragraph.</p></body></html>"
    root = quick_parsehtml(html)
    assert root[0][0].text == "This is a comment."
    assert root[0][1].tag == "p"
    assert root[0][1].text == "This is a paragraph."


def test_missing_end_tag():
    # Test for a missing 'a' end tag
    html = "<html><body><a href='http://google.ie/'>link</body></html>"
    root = quick_parsehtml(html)
    assert root.find(".//a").get("href") == "http://google.ie/"
    assert Etree.tostring(root, method="html") == b'<html><body><a href="http://google.ie/">link</a></body></html>'


def test_extra_tag():
    # Check that a extra tag that should not exist was removed
    html = "<html><body></div></body></html>"
    root = quick_parsehtml(html)
    assert len(root[0]) == 0
    assert Etree.tostring(root, method="html") == b'<html><body></body></html>'


def test_find_empty_attribute():
    # Check whether we can find an element with an empty-valued attribute
    html = "<html><body><form autofocus><input type='checkbox' checked></form></body></html>"
    form = quick_parse_filter(html, "form", {"autofocus": True})
    assert "autofocus" in form.attrib
    assert form.find(".//input[@checked]") is not None


# ############################# HTML Entity ############################## #


def test_entity_name_euro():
    html = "<html><body>cost is &euro;49.99</body></html>"
    root = quick_parsehtml(html)
    assert root[0].text == "cost is €49.99"


def test_entity_number_euro():
    html = "<html><body>cost is &#8364;49.99</body></html>"
    root = quick_parsehtml(html)
    assert root[0].text == "cost is €49.99"


def test_entity_hex_euro():
    html = "<html><body>cost is &#x20AC;49.99</body></html>"
    root = quick_parsehtml(html)
    assert root[0].text == "cost is €49.99"


def test_entity_name_euro_fail():
    html = "<html><body>cost is &euros;49.99</body></html>"
    root = quick_parsehtml(html)
    assert "euros" in root[0].text


def test_entity_hex_euro_fail():
    html = "<html><body>cost is &#xDB9900;49.99</body></html>"
    root = quick_parsehtml(html)
    assert "€" not in root[0].text


# ############################# Text Content ############################# #


def test_text_iterator():
    html = "<html><body>sample text content</body></html>"
    root = quick_parsehtml(html)
    body = root.find(".//body")
    assert "".join(body.itertext()) == "sample text content"


def test_text_iterator_unclosed_tag():
    html = "<html><body><div>hello <span>to <span>the <span>world!</div></body><footer>unrelated</footer></html>"
    root = quick_parsehtml(html)
    body = root.find(".//body")
    assert "".join(body.itertext()) == "hello to the world!"


# ############################# Filter Test ############################## #


def test_tag_match():
    html = "<html><body><div test='attribute'><p>text</p></div></body></html>"
    root = quick_parse_filter(html, "div")
    assert root.tag == "div"
    assert root[0].tag == "p"


def test_tag_no_match():
    html = "<html><body></body></html>"
    with pytest.raises(RuntimeError) as excinfo:
        quick_parse_filter(html, "div")
    excinfo.match("Unable to find requested section with tag of")


def test_attrib_match():
    html = "<html><body><div test='attribute'><p>text</p></div><div test='yes'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"test": "yes"})
    assert root.tag == "div"
    assert root.get("test") == "yes"
    assert root.text == "text"


def test_attrib_no_match():
    html = "<html><body><div><p>text</p></div><div>text</div></body></html>"
    with pytest.raises(RuntimeError) as excinfo:
        quick_parse_filter(html, "div", {"test": "yes"})
    excinfo.match("Unable to find requested section with tag of")


def test_attrib_match_name():
    # Search for any div tag with a attribute of src of any value
    html = "<html><body><div test='attribute'><p>text</p></div><div src='foo bar'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"src": True})
    assert root.tag == "div"
    assert root.get("src")
    assert root.text == "text"


def test_attrib_match_unwanted():
    # Search for a div with a test attribute but not a src attribute
    html = "<html><body><div src='attribute' test='yes'><p>text</p></div><div test='yes'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"test": "yes", "src": False})
    assert root.tag == "div"
    assert root.get("test") == "yes"
    assert "src" not in root.attrib
    assert root.text == "text"


def test_tag_match_badhtml():
    html = "<html><body><div test='attribute'><p>text</div></body></html>"
    root = quick_parse_filter(html, "div")
    assert root.tag == "div"
    assert root[0].tag == "p"


def test_partial_filter():
    # Check that the
    html = "<html><body><div test='attribute'><p>text</p></div></body></html>"
    obj = htmlement.HTMLement("div")
    obj.feed(html[:51])
    obj.feed(html[51:])
    root = obj.close()
    assert root.tag == "div"
    assert root[0].tag == "p"


# ####################### Unicode Decoding Test ####################### #


def test_with_encoding():
    # Check that I can parse a simple tree
    html = b"<html><body></body></html>"
    root = quick_parsehtml(html, encoding="utf-8")
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_no_encoding_with_header_type1(recwarn):
    # Check for charset header type one
    html = b"<html><head><meta charset='utf-8'/></head><body>text</body></html>"
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type2(recwarn):
    # Check for charset header type one
    html = b'<html><head><meta charset="utf-8"/></head><body>text</body></html>'
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type3(recwarn):
    # Check for charset header type one
    html = b"<html><head><meta charset='utf-8'></head><body>text</body></html>"
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type4(recwarn):
    # Check for charset header type one
    html = b'<html><head><meta charset="utf-8"></head><body>text</body></html>'
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type5(recwarn):
    # Check for charset header type one
    html = b"<html><head><meta content='text/html; charset=utf-8'/></head><body>text</body></html>"
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type6(recwarn):
    # Check for charset header type one
    html = b'<html><head><meta content="text/html; charset=utf-8"/></head><body>text</body></html>'
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type7(recwarn):
    # Check for charset header type one
    html = b"<html><head><meta content='text/html; charset=utf-8'></head><body>text</body></html>"
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_with_header_type8(recwarn):
    # Check for charset header type one
    html = b'<html><head><meta content="text/html; charset=utf-8"></head><body>text</body></html>'
    quick_parsehtml(html)
    # Check that no warnings ware raised
    warnmsg = "Unable to determine encoding, defaulting to iso-8859-1"
    for w in recwarn.list:
        assert issubclass(w.category, UnicodeWarning) is False or not w.message == warnmsg


def test_no_encoding_no_header():
    # Check that I can parse a simple tree
    html = b"<html><head></head><body>text</body></html>"
    with pytest.warns(UnicodeWarning):
        quick_parsehtml(html)


# ####################### Funtion Tests ####################### #


def test_fromstring():
    # Check that I can parse a simple tree
    html = "<html><body></body></html>"
    root = htmlement.fromstring(html)
    assert Etree.iselement(root)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_fromstringlist():
    # Check that I can parse a simple tree
    sequence = ["<html><body>", "</body></html>"]
    root = htmlement.fromstringlist(sequence)
    assert Etree.iselement(root)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_parse_file_object():
    html = "<html><body></body></html>"
    fileobj = io.StringIO(html)
    root = htmlement.parse(fileobj, encoding="utf8")
    assert Etree.iselement(root)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_parse_filename():
    # Create temp file and add html data to it
    html = "<html><body></body></html>"
    fileobj = tempfile.NamedTemporaryFile("w", delete=False)
    fileobj.write(html)
    filename = fileobj.name
    fileobj.close()

    try:
        root = htmlement.parse(filename, encoding="utf8")
        assert Etree.iselement(root)
        assert root.tag == "html"
        assert root[0].tag == "body"
    finally:
        os.remove(filename)


# ####################### Examples Tests ####################### #


def test_example_simple():
    # Check that there is no errors
    examples.example_simple()


def test_example_filter():
    # Check that there is no errors
    examples.example_filter()


def test_example_complex():
    # Check that there is no errors
    examples.example_complex()
