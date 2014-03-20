#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import dateutil.parser
import logging
import os
import re
import requests
import simplejson

from flask import Flask, Response, render_template, request
from logging import FileHandler
from wsgiref.handlers import CGIHandler

app = Flask(__name__)

# Avoid default Flask redirect when a
# URL is requested without a final slash
app.url_map.strict_slashes = False

# Stop extra whitespace creeping
# into Jinja templates
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Get the "root" url path, because
# Flask isn't running at the domain root
request_path = os.environ.get('PATH_INFO', '/toolid/token/cgi-bin/rss')
api_path = '/'.join(request_path.split('/')[0:5])
api_server = os.environ.get('HTTP_HOST', 'server.scraperwiki.com')

def get_dataset_url():
    try:
        with open('/home/dataset_url.txt', 'r') as file:
            return file.read()
    except IOError:
        return None

dataset_url = get_dataset_url()

def log_request(logger):
    logger.info("REQUEST: {} [{}] \"{} {} {}\" \"{}\"".format(
        os.environ.get('REMOTE_ADDR', '-').split(':')[0],
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000"),
        os.environ.get('REQUEST_METHOD', '-'),
        os.environ.get('REQUEST_URI', '-'),
        os.environ.get('SERVER_PROTOCOL', '-'),
        os.environ.get('HTTP_USER_AGENT', '-')
    ))


@app.route(api_path + "/feed.rss")
def show_collections():
    resp = Response()
    query = get_query_from_request_args(request.args)
    if query:
        results = get_results(dataset_url, query)
        resp.headers[b'Content-Type'] = b'application/rss+xml;charset=utf-8'
        resp.data = render_template(
            'feed.xml',
            api_server=api_server,
            api_path=api_path,
            results=results
        )
    else:
        resp.status_code = 404
        resp.data = 'You must supply either a "table" parameter or a "query" parameter in your query string'

    return resp


def get_query_from_request_args(args):
    if 'table' in args:
        table = sqlite_escape(args['table'])
        title = 'title'
        link = 'link'
        description = 'description'
        guid = 'guid'
        pubDate = 'pubDate'

        if 'title' in args:
            title = sqlite_escape(args['title'])
        if 'link' in args:
            link = sqlite_escape(args['link'])
        if 'description' in args:
            description = sqlite_escape(args['description'])
        if 'guid' in args:
            guid = sqlite_escape(args['guid'])
        if 'pubDate' in args:
            pubDate = sqlite_escape(args['pubDate'])

        query = 'SELECT "{}", "{}", "{}", "{}", "{}" FROM "{}" ORDER BY "rowid" DESC LIMIT 100'.format(title, link, description, guid, pubDate, table)
        return query
    if 'query' in args:
        return args['query']
    else:
        return None


def get_results(url, query):
    try:
        rows = requests.get(url, params={'q': query}).json()
    except requests.exceptions.RequestException:
        return []
    except simplejson.JSONDecodeError:
        return []

    if isinstance(rows, list):
        return rows
    else:
        return []


def sqlite_escape(string):
    return re.sub(r'"', '""', string)


if __name__ == "__main__":
    # Log exceptions to http/log.txt
    logger = logging.getLogger('rss')
    hdlr = logging.FileHandler('/home/http/log.txt')
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    app.logger.addHandler(hdlr)

    try:
        log_request(logger)
        CGIHandler().run(app)
    except Exception, e:
        logger.exception("EXCEPTION:")
