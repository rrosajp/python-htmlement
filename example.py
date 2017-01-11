#!/usr/bin/env python
from __future__ import print_function, unicode_literals
from htmlement import HTMLement

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
    print(a.get("href"))

# For more information, see:
# https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element
# https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
