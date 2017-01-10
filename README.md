python-htmlparser
=================

Python HTMLParser extension with ElementTree support.


Why another Python HTML Parser?
-----

There is no HTML Parser in the Python Standard Library.
Actually, there is the html.parser.HTMLParser that simply traverses the DOM tree and allows us to be notified as each tag is being parsed.

Usually, when we parse HTML we want to query its elements and extract data from it.
The most simple way to do this is to use XPath expressions.
Python do support a simple (read limited) XPath engine into its ElementTree, but there is no way to parse an HTML document into XHTML and then use this library to query it.

This HTML Parser extends html.parser.HTMLParser returning an xml.etree.Element instance (the root element) which natively supports the ElementTree API.

You may use this code however you like.
You may even copy-paste it into your project in order to keep the result clean and simple (a comment to this source is welcome!).


Example
-----

```python
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

# Root is an xml.etree.Element and supports the ElementTree API
# (e.g. you may use its limited support for XPath expressions)

# Get title
title = root.find('head/title').text
print("Parsing website: %s" % title)

# Get all anchors
for a in root.iterfind(".//a"):
    print(a.get("href"))

# For more information, see:
# https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element
# https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
```

Output:
```
GitHub
https://github.com/marmelo
https://github.com/marmelo/python-htmlparser
```
