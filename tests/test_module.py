#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 2 compatibility
from __future__ import unicode_literals
import xml.etree.ElementTree as Etree
import htmlement
import pytest


def quick_parsehtml(html):
    obj = htmlement.HTMLement()
    obj.feed(html)
    root = obj.close()
    assert Etree.iselement(root)
    return root


def quick_parse_filter(html, tag, attrs=None):
    obj = htmlement.HTMLement(tag, attrs)
    obj.feed(html)
    return obj.close()


def test_initialization():
    # Check that the parser even starts
    obj = htmlement.HTMLement()
    assert isinstance(obj, htmlement.HTMLement)


def test_basic_tree():
    # Check that I can parse a simple tree
    html = "<html><body></body></html>"
    root = quick_parsehtml(html)
    assert root.tag == "html"
    assert root[0].tag == "body"


def test_nohtml_tree():
    # Check the the missing html starting tag is created
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


# ############################# Filter Test ############################## #


def test_tag_match():
    html = "<html><body><div test='attribute'><p>text<p></div></body></html>"
    root = quick_parse_filter(html, "div")
    assert root.tag == "div"
    assert root[0].tag == "p"


def test_tag_no_match():
    html = "<html><body></body></html>"
    with pytest.raises(RuntimeError) as excinfo:
        quick_parse_filter(html, "div")

    excinfo.match("Unable to find requested section with tag of")


def test_attrib_match():
    html = "<html><body><div test='attribute'><p>text<p></div><div test='yes'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"test": "yes"})
    assert root.tag == "div"
    assert root.get("test") == "yes"
    assert root.text == "text"


def test_attrib_no_match():
    html = "<html><body><div><p>text<p></div><div>text</div></body></html>"
    with pytest.raises(RuntimeError) as excinfo:
        quick_parse_filter(html, "div", {"test": "yes"})

    excinfo.match("Unable to find requested section with tag of")


def test_attrib_match_name():
    # Search for any div tag with a attribute of src of any value
    html = "<html><body><div test='attribute'><p>text<p></div><div src='foo bar'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"src": True})
    assert root.tag == "div"
    assert root.get("src")
    assert root.text == "text"


def test_attrib_match_unwanted():
    # Search for a div with a test attribute but not a src attribute
    html = "<html><body><div src='attribute' test='yes'><p>text<p></div><div test='yes'>text</div></body></html>"
    root = quick_parse_filter(html, "div", {"test": "yes", "src": False})
    assert root.tag == "div"
    assert root.get("test") == "yes"
    assert "src" not in root.attrib
    assert root.text == "text"
