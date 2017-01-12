#!/usr/bin/env python
"""
For more information, see:
@see https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element
@see https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
"""
from __future__ import print_function, unicode_literals
from htmlement import HTMLement, TreeFilter


def example_simple():
    html = """
    <html>
      <head>
        <title>GitHub</title>
      </head>
      <body>
        <a href="https://github.com/willforde">GitHub</a>
        <a href="https://github.com/willforde/python-htmlement">GitHub Project</a>
      </body>
    </html>
    """

    # Parse the document
    parser = HTMLement()
    root = parser.parse(html)

    # Root is an xml.etree.Element and supports the ElementTree API
    # (e.g. you may use its limited support for XPath expressions)

    # Get title
    title = root.find('head/title').text
    print("Parsing: %s" % title)

    # Get all anchors
    for a in root.iterfind(".//a"):
        # Get href attribute from anchor
        url = a.get("href")
        print(url)


def example_filter():
    html = """
    <html>
      <head>
        <title>Coffee shop</title>
      </head>
      <body>
        <ul class="menu">
          <li>Coffee</li>
          <li>Tea</li>
          <li>Milk</li>
        </ul>
      </body>
    </html>
    """

    # Parse the document
    parser = HTMLement()
    sec_filter = TreeFilter("ul", attrs={"class": "menu"})
    root = parser.parse(html, tree_filter=sec_filter)

    # Root should now be a 'ul' xml.etree.Element with all it's child elements available
    # All other elements have been ignored. Way faster to parse.

    # We are unable to get the title here sense all
    # elements outside the filter was ignored

    # Get all listitems
    for item in root.iterfind("./li"):
        # Get text from listitem
        print(item.text)

if __name__ == "__main__":
    example_simple()
    example_filter()
