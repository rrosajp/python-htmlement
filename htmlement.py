#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 2 compatibility
from __future__ import unicode_literals

# Standard library imports
import warnings
import sys
import re

# Import the faster C implementation of ElementTree whenever available
try:
    from xml.etree import cElementTree as Etree
except ImportError:
    from xml.etree import ElementTree as Etree

# Check python version to set the object that can detect non unicode strings
if sys.version_info >= (3, 0):
    # noinspection PyCompatibility
    from html.parser import HTMLParser
    basestring = (bytes, str)
else:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyCompatibility
    from HTMLParser import HTMLParser

__all__ = ["HTMLement", "fromstring", "fromstringlist", "parse", "make_unicode", "HTMLParseError"]
__version__ = "0.1"


def fromstring(text, tag=None, attrs=None):
    """
    Parses an HTML document from a string into an element tree.

    :param str text: The HTML document to parse.
    :param str tag: see :class:`HTMLement`.
    :param dict attrs: see :class:`HTMLement`.

    :return: The root element of the element tree.
    :rtype: xml.etree.ElementTree.Element

    :raises HTMLParseError: If parsing of HTML document fails.
    """
    parser = HTMLement(tag, attrs)
    parser.feed(text)
    return parser.close()


def fromstringlist(sequence, tag=None, attrs=None):
    """
    Parses an HTML document from a sequence of html segments into an element tree.

    :param list sequence: A sequence of HTML segments to parse.
    :param str tag: see :class:`HTMLement`.
    :param dict attrs: see :class:`HTMLement`.

    :return: The root element of the element tree.
    :rtype: xml.etree.ElementTree.Element

    :raises HTMLParseError: If parsing of HTML document fails.
    """
    parser = HTMLement(tag, attrs)
    for text in sequence:
        parser.feed(text)
    return parser.close()


def parse(source, tag=None, attrs=None):
    """
    Load an external HTML document into element tree.

    :param source: A filename or file object containing HTML data.
    :param str tag: see :class:`HTMLement`.
    :param dict attrs: see :class:`HTMLement`.

    :return: The root element of the element tree.
    :rtype: xml.etree.ElementTree.Element

    :raises HTMLParseError: If parsing of HTML document fails.
    """
    # Assume that source is a file pointer if no read methods is found
    if hasattr(source, "read"):
        source = open(source, "rb")
        close_source = True
    else:
        close_source = False

    try:
        parser = HTMLement(tag, attrs)
        while True:
            # Read in 64k at a time
            data = source.read(65536)
            if not data:
                break

            # Feed the parser
            parser.feed(data)

        # Return the root element
        return parser.close()

    finally:
        if close_source:
            source.close()


def make_unicode(source, encoding=None, default_encoding="iso-8859-1"):
    """
    Convert *source* from type bytes to type str, if not already str.

    If *source* is not of type *str* and *encoding* was not specified then the encoding
    will be extracted from *source* using meta tags if available.
    Will default to *default_encoding* if unable to find *encoding*.

    :param bytes source: The html document.
    :param str encoding: (optional) The encoding used to convert *source* to *str*.
    :param str default_encoding: (optional) Default encoding to use when unable to extract the encoding from *source*.

    :return: HTML data decoded into str(unicode).
    :rtype: str

    :raises UnicodeDecodeError: If decoding of *source* fails.
    :raises ValueError: If *source* is not of type *bytes* or *str*.
    """
    if isinstance(source, basestring):
        if not isinstance(source, bytes):
            # Already str(unicode)
            return source
    else:
        raise ValueError("Source is not of valid type bytes or str")

    if encoding is None:
        # Atemp to find the encoding from the html source
        end_head_tag = source.find(b"</head>")
        if end_head_tag:
            # Search for the charset attribute within the meta tags
            charset_refind = b'<meta.+?charset=[\'"]*(.+?)["\'].*?>'
            charset = re.search(charset_refind, source[:end_head_tag], re.IGNORECASE)
            if charset:
                encoding = charset.group(1)
            else:
                warn_msg = "Unable to determine encoding, defaulting to {}".format(default_encoding)
                warnings.warn(warn_msg, UnicodeWarning, stacklevel=1)
        else:
            warn_msg = "Unable to determine encoding, defaulting to {}".format(default_encoding)
            warnings.warn(warn_msg, UnicodeWarning, stacklevel=1)

    # Decode the string into unicode
    return source.decode(encoding if encoding else default_encoding)


# Required for raiseing HTMLParseError in python3, emulates python2
class HTMLParseError(Exception):
    """Exception raised for all parse errors."""
    def __init__(self, msg, position=(None, None)):
        self.msg = msg
        self.lineno = position[0]
        self.offset = position[1]

    def __str__(self):
        result = self.msg
        if self.lineno is not None:
            result += ", at line %d" % self.lineno
        if self.offset is not None:
            result += ", column %d" % self.offset
        return result


class HTMLement(object):
    """
    Python HTMLParser extension with ElementTree Parser support.

    This HTML Parser extends :class:`html.parser.HTMLParser` returning an :class:`xml.etree.ElementTree.Element`
    instance. The returned root element natively supports the ElementTree API.
    (e.g. you may use its limited support for `XPath expressions`__)

    .. _Xpath: https://docs.python.org/3.6/library/xml.etree.elementtree.html#xpath-support
    __ XPath_
    """
    def __init__(self, tag=None, attrs=None):
        self._parser = _ParseHTML(tag, attrs)
        self.finished = False

    def feed(self, data):
        """
        Feeds data to the parser.

        :param str data: HTML data
        :raises ValueError: If *data* is not of type str.
        """
        # Skip feeding data into parser if we already have what we want
        if self.finished is True:
            return None

        # Make sure that we have unicode before continuing
        if isinstance(data, bytes):
            raise ValueError("HTML source must be str(unicode) not bytes. Please feed me unicode")

        # Parse the html document
        try:
            self._parser.feed(data)
        except EOFError:
            self.finished = True
            self._parser.reset()

    def close(self):
        """
        Close the tree builder and return the root element of the element tree.

        :return: The root element of the element tree.
        :rtype: xml.etree.ElementTree.Element
        """
        return self._parser.close()


class _ParseHTML(HTMLParser):
    def __init__(self, tag, attrs):
        # Initiate HTMLParser
        HTMLParser.__init__(self)
        self.convert_charrefs = True
        self._root = None  # root element
        self._data = []  # data collector
        self._factory = Etree.Element

        # Split attributes into wanted and unwanted attributes
        self._unw_attrs = [attrs.pop(key) for key, value in attrs.items() if value is False] if attrs else []
        self.attrs = attrs if attrs else {}
        self.enabled = not tag
        self.tag = tag

        # Some tags in html do not require closing tags so thoes tags will need to be auto closed (Void elements)
        # Refer to: https://www.w3.org/TR/html/syntax.html#void-elements
        self._voids = frozenset(("area", "base", "br", "col", "hr", "img", "input", "link", "meta", "param",
                                 # Only in HTML5
                                 "embed", "keygen", "source", "track",
                                 # Not supported in HTML5
                                 "basefont", "frame", "isindex",
                                 # SVG self closing tags
                                 "rect", "circle", "ellipse", "line", "polyline", "polygon",
                                 "path", "stop", "use", "image", "animatetransform"))

        # Create temporary root element to protect from badly written sites that either
        # have no html starting tag or multiple top level elements
        elem = self._factory("html")
        self._elem = [elem]
        self._last = elem
        self._tail = 0

    def handle_starttag(self, tag, attrs):
        self._handle_starttag(tag, attrs, self_closing=tag in self._voids)

    def handle_startendtag(self, tag, attrs):
        self._handle_starttag(tag, attrs, self_closing=True)

    def _handle_starttag(self, tag, attrs, self_closing=False):
        enabled = self.enabled
        # Add tag element to tree if we have no filter or that the filter matches
        if enabled or self._search(tag, attrs):
            # Convert attrs to dictionary
            attrs = dict(attrs) if attrs else {}
            self._flush()

            # Create the new element
            elem = self._factory(tag, attrs)
            self._elem[-1].append(elem)
            self._last = elem

            # Only append the element to the list of elements if it's not a self closing element
            if self_closing:
                self._tail = 1
            else:
                self._elem.append(elem)
                self._tail = 0

            # Set this element as the root element when the filter search matches
            if not enabled:
                self._root = elem
                self.enabled = True

    def handle_endtag(self, tag):
        # Only process end tags when we have no filter or that the filter has been matched
        if self.enabled and tag not in self._voids:
            _elem = self._elem
            _root = self._root
            # Check that the closing tag is what's actualy expected
            if _elem[-1].tag == tag:
                self._flush()
                self._tail = 1
                self._last = elem = _elem.pop()
                if elem is _root:
                    raise EOFError

            # If the previous element is what we actually have then the expected element was not
            # properly closed so we must close that before closing what we have now
            elif len(_elem) >= 2 and _elem[-2].tag == tag:
                self._flush()
                self._tail = 1
                for _ in range(2):
                    self._last = elem = _elem.pop()
                    if elem is _root:
                        raise EOFError
            else:
                # Unable to match the tag to an element, ignoring it
                return None

    def handle_data(self, data):
        data = data.strip()
        if data and self.enabled:
            self._data.append(data)

    def handle_comment(self, data):
        data = data.strip()
        if data and self.enabled:
            elem = Etree.Comment(data)
            self._elem[-1].append(elem)

    def close(self):
        self._flush()
        if self._root is not None:
            return self._root
        else:
            # Search the root element to find a proper html root element if one exists
            tmp_root = self._elem[0]
            proper_root = tmp_root.find("html")
            if proper_root is None:
                # Not proper root was found
                return tmp_root
            else:
                # Proper root found
                return proper_root

    def error(self, message):
        raise HTMLParseError(message, self.getpos())

    def _flush(self):
        if self._data:
            if self._last is not None:
                text = "".join(self._data)
                if self._tail:
                    self._last.tail = text
                else:
                    self._last.text = text
            self._data = []

    def _search(self, tag, attrs):
        # Only search when the tag matches
        if tag == self.tag:
            # If we have required attrs to match then search all attrs for wanted attrs
            # And also check that we do not have any attrs that are unwanted
            if self.attrs or self._unw_attrs:
                if attrs:
                    wanted_attrs = self.attrs.copy()
                    unwanted_attrs = self._unw_attrs
                    for key, value in attrs:
                        # Check for unwanted attrs
                        if key in unwanted_attrs:
                            return False

                        # Check for wanted attrs
                        elif key in wanted_attrs:
                            c_value = wanted_attrs[key]
                            if c_value == value or c_value is True:
                                # Remove this attribute from the wanted dict of attributes
                                # to indicate that this attribute has been found
                                del wanted_attrs[key]

                    # If wanted_attrs is now empty then all attributes must have been found
                    if not wanted_attrs:
                        return True
            else:
                # We only need to match tag
                return True

        # Unable to find required section
        return False
