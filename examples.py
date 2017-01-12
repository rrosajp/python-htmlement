#!/usr/bin/env python
"""
For more information, see:
@see https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element
@see https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
"""
from __future__ import print_function, unicode_literals
from htmlement import HTMLement, TreeFilter


def example_simple():
    """
    This example will parse a simple html tree and
    extract the website title and all anchors

    >>> example_simple()
    Parsing: GitHub
    GitHub => https://github.com/willforde
    GitHub Project => https://github.com/willforde/python-htmlement
    """
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
    print("Parsing: {}".format(title))

    # Get all anchors
    for a in root.iterfind(".//a"):
        # Get href attribute
        url = a.get("href")
        # Get anchor name
        name = a.text

        print("{} => {}".format(name, url))


def example_filter():
    """
    This example will parse a simple html tree and
    extract all the list items within the ul menu element using a tree filter.

    The tree filter will tell the parser to only parse the elements within the
    requested section and to ignore all other elements.
    Useful for speeding up the parsing of html pages.

    >>> example_filter()
    Coffee
    Tea
    Milk
    """
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
    parser = HTMLement()
    menu_filter = TreeFilter("ul", attrs={"class": "menu"})
    root = parser.parse(html, tree_filter=menu_filter)

    # Root should now be a 'ul' xml.etree.Element with all it's child elements available
    # All other elements have been ignored. Way faster to parse.

    # We are unable to get the title here sense all
    # elements outside the filter was ignored
    print("Menu Items")

    # Get all listitems
    for item in root.iterfind(".//li"):
        # Get text from listitem
        print("- {}".format(item.text))


def example_complex():
    """
    This example will parse a more complex html tree of python talk's and will
    extract the image, title, url and date of each talk.

    A filter will be used to extract the main talks div element

    >>> example_complex()
    Image = /presentations/c7f1fbb5d03a409d9de8abb5238d6a68/thumb_slide_0.jpg
    Url = /pycon2016/alex-martelli-exception-and-error-handling-in-python-2-and-python-3
    Title = Alex Martelli - Exception and error handling in Python 2 and Python 3
    Date = Jun 1, 2016

    Image = /presentations/eef8ffe5b6784f7cb84948cf866b2608/thumb_slide_0.jpg
    Url = /presentations/518cae54da12460e895163d809e25933/thumb_slide_0.jpg
    Title = Jake Vanderplas - Statistics for Hackers
    Date = May 29, 2016

    Image = /presentations/8b3ee51b5fcc4a238c4cb4b7787979ac/thumb_slide_0.jpg
    Url = /pycon2016/brett-slatkin-refactoring-python-why-and-how-to-restructure-your-code
    Title = Brett Slatkin - Refactoring Python: Why and how to restructure your code
    Date = May 29, 2016
    """
    html = """
    <html>
      <head>
        <title>PyCon 2016</title>
      </head>
      <body>
        <div class="main">
          <h1>Talks by PyCon 2016</h1>
          <div class="talks">
            <div class="talk" data-id="c7f1fbb5d03a409d9de8abb5238d6a68">
              <a href="/pycon2016/kelsey-gilmore-innis-seriously-strong-security-on-a-shoestring">
                <img src="/presentations/c7f1fbb5d03a409d9de8abb5238d6a68/thumb_slide_0.jpg">
              </a>
              <div class="talk-listing-meta">
                <h3 class="title">
                  <a href="/pycon2016/alex-martelli-exception-and-error-handling-in-python-2-and-python-3">
                    Alex Martelli - Exception and error handling in Python 2 and Python 3
                  </a>
                </h3>
                <p class="date">Jun 1, 2016</p>
              </div>
            </div>
            <div class="talk" data-id="518cae54da12460e895163d809e25933">
              <a href="/pycon2016/manuel-ebert-putting-1-million-new-words-into-the-dictionary">
                <img src="/presentations/eef8ffe5b6784f7cb84948cf866b2608/thumb_slide_0.jpg">
              </a>
              <div class="talk-listing-meta">
                <h3 class="title">
                  <a href="/presentations/518cae54da12460e895163d809e25933/thumb_slide_0.jpg">
                    Jake Vanderplas - Statistics for Hackers
                  </a>
                </h3>
                <p class="date">May 29, 2016</p>
              </div>
            </div>
            <div class="talk" data-id="8b3ee51b5fcc4a238c4cb4b7787979ac">
              <a href="/pycon2016/brett-slatkin-refactoring-python-why-and-how-to-restructure-your-code">
                <img src="/presentations/8b3ee51b5fcc4a238c4cb4b7787979ac/thumb_slide_0.jpg">
              </a>
              <div class="talk-listing-meta">
                <h3 class="title">
                  <a href="/pycon2016/brett-slatkin-refactoring-python-why-and-how-to-restructure-your-code">
                    Brett Slatkin - Refactoring Python: Why and how to restructure your code
                  </a>
                </h3>
                <p class="date">May 29, 2016</p>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """

    # Parse the document
    parser = HTMLement()
    talks_filter = TreeFilter("div", attrs={"class": "talks"})
    root = parser.parse(html, tree_filter=talks_filter)

    # Extract all div tags with class of talk
    for talk in root.iterfind("./div[@class='talk']"):
        # Fetch image
        img = talk.find(".//img").get("src")
        print("Image = {}".format(img))

        # Fetch title and url
        title_anchor = talk.find("./div/h3/a")
        url = title_anchor.get("href")
        print("Url = {}".format(url))
        title = title_anchor.text
        print("Title = {}".format(title))

        # Fetch date
        date = talk.find("./div/p").text
        print("Date = {}".format(date))
        print("")

if __name__ == "__main__":
    example_simple()
    print("")
    example_filter()
    print("")
    example_complex()
