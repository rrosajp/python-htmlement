from __future__ import print_function, unicode_literals
# noinspection PyCompatibility
try:
    from urllib import request as urllib2
except ImportError:
    import urllib2

from htmlement import HTMLement
import time, hashlib, os, sys
from bs4 import BeautifulSoup


def urlopen(uri, data=None, headers=None, refresh=False, cache_only=False):
    # Convert uri into hash string
    urlhash = hashlib.sha224(uri.encode("utf8")).hexdigest()
    filename = os.path.join("cache", "%s.html" % urlhash)
    if not os.path.exists("cache"):
        os.mkdir("cache")

    # Return cached _children if found
    if refresh is False and os.path.exists(filename):
        with open(filename, "rb") as stream:
            return stream.read().decode("utf8")

    elif cache_only is True:
        raise ValueError

    else:
        # Fetch a new copy from the remote server
        req = urllib2.Request(uri, data=data, headers=headers if headers is not None else {})
        req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0")
        opened = urllib2.urlopen(req)
        html_source = opened.read()
        header = opened.info()
        encoding = header.getparam("charset")
        if encoding is None:
            encoding = "utf8"
        opened.close()

        # Convert html into utf8
        uhtml = html_source.decode(encoding)

        with open(filename, "wb") as stream:
            stream.write(uhtml.encode("utf8"))
        return uhtml


def test_parse_links(url):
    # Fetch the page html source
    html = urlopen(url)

    # Parse the html document
    parser = HTMLement()
    root = parser.parse(html.read())

    # root is an xml.etree.Element and supports the ElementTree API
    # (e.g. you may use its limited support for XPath expressions)

    # Fetch title of site
    title = root.find('head/title').text
    print("Parsing links for website: %s" % title)

    # Parse for a the links on the site
    for atag in root.iterfind(".//a"):
        # Get the href attribute from the a tag element
        print(atag.get("href"))

    print()


def test_elem_v_soup():
    total_saved = []
    total_soup = []
    total_tree = []
    urls = ["https://www.google.ie",
            "https://www.youtube.com/",
            "https://www.facebook.com/",
            "https://www.yahoo.com/",
            "https://www.wikipedia.org/",
            "https://www.linkedin.com/",
            "https://twitter.com/",
            "https://www.amazon.com/",
            "http://www.bing.com/",
            "http://www.ebay.com/",
            "http://www.msn.com/",
            "https://www.microsoft.com/",
            "https://www.pinterest.com/",
            "http://ask.com"]

    for url in urls:
        html = urlopen(url)

        # Test soup
        start = time.time()
        BeautifulSoup(html, "html.parser")
        soup_elasped = time.time() - start
        total_soup.append(soup_elasped)

        # Test tree builder
        start = time.time()
        parser = HTMLement()
        root = parser.parse(html)
        tree_elasped = time.time() - start
        total_tree.append(tree_elasped)

        # Print the time results
        time_saved = soup_elasped - tree_elasped
        print("Soup: %f => tree: %f => Saved: %f" % (soup_elasped, tree_elasped, time_saved))
        total_saved.append(time_saved)

    # Print the average amount of time saved
    print("Average Saved: %f" % (sum(total_saved) / len(total_saved)))
    print("Total Saved: %f" % sum(total_saved))
    print("Total Soup: %f" % sum(total_soup))
    print("Total Tree: %f" % sum(total_tree))

if __name__ == "__main__":
    #test_parse_links("https://github.com")
    test_elem_v_soup()
