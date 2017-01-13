#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2013 Rafael Marmelo
Copyright (c) 2016 William Forde

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
    type_string = bytes
else:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyCompatibility
    from HTMLParser import HTMLParser
    type_string = str


def _make_unicode(source, encoding):
    # Atemp to find the encoding from the html source
    if encoding is None:
        end_head_tag = source.find(b"</head>")
        if end_head_tag:
            # Search for the charset attribute within the meta tags
            charset_refind = b'<meta.+?charset=[\'"]*(.+?)["\'].*?>'
            charset = re.search(charset_refind, source[:end_head_tag], re.IGNORECASE)
            if charset:
                encoding = charset.group(1)
            else:
                warn_msg = "Unable to determine encoding, please specify encoding, defaulting to iso-8859-1"
                warnings.warn(warn_msg, UnicodeWarning, stacklevel=3)
        else:
            warn_msg = "Unable to determine encoding, please specify encoding, defaulting to iso-8859-1"
            warnings.warn(warn_msg, UnicodeWarning, stacklevel=3)

    # Decode the string into unicode
    return source.decode(encoding if encoding else "iso-8859-1")


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


class TreeFilter(object):
    def __init__(self, tag, attrs=None):
        # Split attributes into wanted and unwanted attributes
        self._unw_attrs = [attrs.pop(key) for key, value in attrs.items() if value is False] if attrs else []
        self.found = False
        self.attrs = attrs if attrs else {}
        self.tag = tag

    def search(self, tag, attrs):
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

    # Python 3
    def __bool__(self):
        return self.found

    # Python 2
    def __nonzero__(self):
        return self.found


class HTMLement(object):
    """
    Python HTMLParser extension with ElementTree support.
    @see https://github.com/willforde/python-htmlement

    This HTML Parser extends html.parser.HTMLParser returning an xml.etree.ElementTree.Element instance.
    The returned root element natively supports the ElementTree API.
    (e.g. you may use its limited support for XPath expressions)

    @see https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element
    @see https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
    """
    def __init__(self, tag=None, attrs=None):
        self._parser = ParseHTML(tag, attrs)
        self.finished = False

    def feed(self, source, encoding=None):
        # Skip feeding data into parser if we already have what we want
        if self.finished is True:
            return None

        # Convert source to unicode if not already unicode
        if isinstance(source, type_string):
            source = _make_unicode(source, encoding)

        # Parse the html document
        try:
            self._parser.feed(source)
        except EOFError:
            self.finished = True
            self._parser.reset()

    def close(self):
        # Close the tree builder and return the root element that is returned by the treebuilder
        return self._parser.close()


class ParseHTML(HTMLParser):
    def __init__(self, tag, attrs):
        # Initiate HTMLParser
        HTMLParser.__init__(self)
        self._root = None  # root element
        self._data = []  # data collector
        self._factory = Etree.Element
        self._filter = TreeFilter(tag, attrs) if tag else True

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

    def handle_starttag(self, tag, attrs, self_closing=False):
        _filter = self._filter
        # Add tag element to tree if we have no filter or that the filter matches
        if _filter or _filter.search(tag, attrs):
            # Convert attrs to dictionary
            attrs = dict(attrs) if attrs else {}
            self._flush()

            # Create the new element
            elem = self._factory(tag, attrs)
            self._elem[-1].append(elem)
            self._last = elem

            # Only append the element to the list of elements if it's not a self closing element
            if self_closing or tag in self._voids:
                self._tail = 1
            else:
                self._elem.append(elem)
                self._tail = 0

            # Set this element as the root element when the filter search matches
            if not _filter:
                self._root = elem
                _filter.found = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        # Only process end tags when we have no filter or that the filter has been matched
        if self._filter and tag not in self._voids:
            _elem = self._elem
            _root = self._root
            # Check that the closing tag is what's actualy expected
            if _elem[-1].tag == tag:
                self._flush()
                self._tail = 1
                self._last = elem = _elem.pop()
                if _root and elem is _root:
                    raise EOFError

            # If the previous element is what we actually have then the expected element was not
            # properly closed so we must close that before closing what we have now
            elif len(_elem) >= 2 and _elem[-2].tag == tag:
                self._flush()
                self._tail = 1
                for i in range(2):
                    self._last = elem = _elem.pop()
                    if _root and elem is _root:
                        raise EOFError
            else:
                # Unable to match the tag to an element, ignoring it
                return None

    def handle_data(self, data):
        data = data.strip()
        if data and self._filter:
            self._data.append(data)

    def handle_comment(self, data):
        data = data.strip()
        if data and self._filter:
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
