.. image:: https://api.codacy.com/project/badge/Grade/6b46406e1aa24b95947b3da6c09a4ab5
    :target: https://www.codacy.com/app/willforde/python-htmlement?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=willforde/python-htmlement&amp;utm_campaign=Badge_Grade

Installation
------------
::

    pip install htmlement

-or- ::

    pip install git+https://github.com/willforde/python-htmlement.git

Why another Python HTML Parser?
-------------------------------

There is no HTML Parser in the Python Standard Library.
Actually, there is the :class:`html.parser.HTMLParser` that simply traverses the DOM tree and allows us to be notified as
each tag is being parsed. Usually, when we parse HTML we want to query its elements and extract data from it.

There are a few third party HTML parsers available like "lxml", "html5lib" and "beautifulsoup".
    * lxml is the best parser available, fast and reliable but sense it requires C libraries, it's not always possible to install.
    * html5lib is a pure-python library and is designed to conform to the WHATWG HTML specification. But it is very slow at parsing HTML.
    * beautifulsoup is also a pure-python library but is considered by most to be very slow as well.

The aim of this project is to be a pure-python HTML parser that is also faster than beautifulsoup.
The most simple way to do this is to use `XPath expressions`__.
Python does support a simple (read limited) XPath engine inside its ElementTree module.
Also a nice benefit of using ElementTree is that it can use a C implementation whenever available.

This HTML Parser extends :class:`html.parser.HTMLParser` to build a tree of :class:`ElementTree.Element <xml.etree.ElementTree.Element>` instances.
The returned root element natively supports the ElementTree API.


Parsing HTML
------------
Here we’ll be using a sample HTML document that we will parse using htmlement:
::

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

    # Parse the document
    import htmlement
    root = htmlement.fromstring(html)

Root is an :class:`ElementTree.Element <xml.etree.ElementTree.Element>` and supports the ElementTree API
with XPath expressions. With this we are easily able to get both the title and all anchors in the document.
::

    # Get title
    title = root.find("head/title").text
    print("Parsing: %s" % title)

    # Get all anchors
    for a in root.iterfind(".//a"):
        print(a.get("href"))

And the output should be like this:
::

    Parsing: GitHub
    https://github.com/willforde
    https://github.com/willforde/python-htmlement


Parsing HTML with a filter
--------------------------
Here we’ll be using a slightly more complex HTML document that we will parse using htmlement with a filter to fetch
only the menu items. This can be very useful when dealing with large HTML documents sense it can be quite slow to parse
a whole document when we only need to parse a small part of it.
::

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
        <ul class="extras">
          <li>Sugar</li>
          <li>Cream</li>
        </ul>
      </body>
    </html>
    """

    # Parse the document
    import htmlement
    root = htmlement.fromstring(html, "ul", attrs={"class": "menu"})

In this case we are unable to get the title sense all elements outside the filter ware ignored.
But this allows us to be able to extract all listitem elements within the menu list and nothing else.
::

    # Get all listitems
    for item in root.iterfind(".//li"):
        # Get text from listitem
        print(item.text)

And the output should be like this:
::

    Coffee
    Tea
    Milk

.. seealso::
    More examples can be found in examples.py_.


.. _Xpath: https://docs.python.org/3.6/library/xml.etree.elementtree.html#xpath-support
__ XPath_

.. _examples.py: https://github.com/willforde/python-htmlement/blob/master/examples.py
