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
        response = self.app.get('/toolid/token/cgi-bin/rss/feed.rss?table=example')
        dom = lxml.html.fromstring(response.data)
        assert_equal(response.status_code, 200)
        assert_equal(len(dom.cssselect('channel')), 1)

    def test_feed_returns_error_if_missing_table_parameter(self):
        response = self.app.get('/toolid/token/cgi-bin/rss/feed.rss')
        assert_equal(response.status_code, 404)
        assert_in(response.data, 'You must supply a "table" parameter in your query string')

    def test_feed_returns_valid_xml_if_custom_sql_query_provided(self):
        response = self.app.get('/toolid/token/cgi-bin/rss/feed.rss?query=select+*+from+example')
        dom = lxml.html.fromstring(response.data)
        assert_equal(response.status_code, 200)
        assert_equal(len(dom.cssselect('channel')), 1)
