# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import unittest
import tempfile
import mock
import os
import lxml.html

from collections import OrderedDict
from nose.tools import *
from flask import Response

import rss # this is our Flask script


class CgiTestCase(unittest.TestCase):

    def setUp(self):
        rss.app.config['TESTING'] = True
        self.app = rss.app.test_client()

    def test_feed_returns_valid_xml(self):
        response = self.app.get('/toolid/token/cgi-bin/rss/feed.rss')
        dom = lxml.html.fromstring(response.data)
        assert_equal(len(dom.cssselect('channel')), 1)
