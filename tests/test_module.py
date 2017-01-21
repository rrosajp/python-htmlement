#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 2 compatibility
from __future__ import unicode_literals

import xml.etree.ElementTree as Etree
import htmlement


def test_example_simple():
    root = htmlement.fromstring("<html><body><p>testing</p></body></html>")
    assert Etree.iselement(root)
