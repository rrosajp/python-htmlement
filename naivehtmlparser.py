#!/usr/bin/env python
"""
Python 3.x HTMLParser extension with ElementTree support.
"""

from html.parser import HTMLParser
from xml.etree import ElementTree


class NaiveHTMLParser(HTMLParser):
    """
    Python 3.x HTMLParser extension with ElementTree support.
    @see https://github.com/marmelo/python-htmlparser
    """

    def __init__(self):
        self.root = None
        self.tree = ElementTree.TreeBuilder()
        HTMLParser.__init__(self)

    def feed(self, data):
        HTMLParser.feed(self, data)
        self.root = self.tree.close()
        return self.root

    def handle_starttag(self, tag, attrs):
        self.tree.start(tag, dict(self.__filter_attrs(attrs)))

    def handle_endtag(self, tag):
        self.tree.end(tag)

    def handle_data(self, data):
        self.tree.data(data)

    def get_root_element(self):
        return self.root

    def __filter_attrs(self, attrs):
        return filter(lambda x: x[0] and x[1], attrs) if attrs else []


# example usage
if __name__ == "__main__":

    html = """
    <html>
      <head>
        <title>GitHub</title>
      </head>
      <body>
        <a href="https://github.com/marmelo">GitHub</a>
        <a href="https://github.com/marmelo/python-htmlparser">GitHub Project</a>
      </body>
    </html>
    """

    parser = NaiveHTMLParser()
    root = parser.feed(html)
    parser.close()

    # root is an xml.etree.Element and supports the ElementTree API
    # (e.g. you may use its limited support for XPath expressions)

    # get title
    print(root.find('head/title').text)

    # get all anchors
    for a in root.findall('.//a'):
        print(a.get('href'))

    # for more information, see:
    # https://docs.python.org/3.3/library/xml.etree.elementtree.html
    # https://docs.python.org/3.3/library/xml.etree.elementtree.html#xpath-support
    # https://docs.python.org/3.3/library/xml.etree.elementtree.html#treebuilder-objects
