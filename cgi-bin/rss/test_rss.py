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
        assert_in(response.data, 'You must supply either a "table" parameter or a "query" parameter in your query string')

    def test_feed_returns_valid_xml_if_custom_sql_query_provided(self):
        response = self.app.get('/toolid/token/cgi-bin/rss/feed.rss?query=select+*+from+example')
        dom = lxml.html.fromstring(response.data)
        assert_equal(response.status_code, 200)
        assert_equal(len(dom.cssselect('channel')), 1)


class ExecutingQueries(unittest.TestCase):

    @raises(TypeError)
    def test_get_results_raises_exception_if_url_is_omitted(self):
        rss.get_results()

    @raises(TypeError)
    def test_get_results_raises_exception_if_query_is_omitted(self):
        url = 'https://server.scraperwiki.com/datasetid/token/sql'
        rss.get_results(url)

    @mock.patch('requests.get')
    def test_get_results_calls_sql_endpoint(self, requests_get):
        url = 'https://server.scraperwiki.com/datasetid/token/sql'
        query = 'select * from my_table limit 100'
        results = rss.get_results(url, query)
        assert requests_get.called
        requests_get.assert_called_with(url, params={"q": query})

    def test_get_results_returns_a_list(self):
        url = 'https://server.scraperwiki.com/datasetid/token/sql'
        query = 'select * from my_table limit 100'
        results = rss.get_results(url, query)
        print type(results)
        assert isinstance(results, list)
