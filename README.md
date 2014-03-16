# Publish with RSS

A ScraperWiki tool for constructing RSS feeds based on your data. It is based heavily on the “Connect with OData” tool.

## How it works

When the tool is first installed, it records the source dataset url and `pip install`s Flask. The RSS feed is generated via a CGI script on each request, using the supplied query string parameters.

## Getting the right data

The “Publish with RSS” tool needs to be told which table in the source dataset you want to get data from, and which columns it should use for the `<title>`, `<link>`, `<description>`, `<guid>`, and `<pubDate>` fields of each channel item.

These settings are provided as query string parameters in the feed URL. If `title`, `link`, `description`, `guid`, and `pubDate` parameters are omitted, the tool will automatically assume the default column names of `title`, `link`, `description`, `guid`, and `pubDate` and request those from the given table.

So, the simplest feed URL this tool supports would be something like:

```
https://server.scraperwiki.com/box/publishtoken/cgi-bin/rss/feed.rss?table=twitter_followers
```

You can specify a custom limit on the number of items returned (the default is 100), and a custom sort order (the default is the `rowid` column, descending) by supplying suitable query string parameters:

```
https://server.scraperwiki.com/box/publishtoken/cgi-bin/rss/feed.rss?table=twitter_followers&limit=5&sort=pubDate,+asc
```

If the source table doesn’t contain `title`, `link`, `description`, `guid`, and `pubDate` columns, custom selectors must be supplied:

```
https://server.scraperwiki.com/box/publishtoken/cgi-bin/rss/feed.rss?table=twitter_followers&title=screen_name&link=…
```

There are certain situations where you want ultimate flexibility over the tables and columns published in your feed. For example, you might want to use a SQL `JOIN` statement rather than selecting directly from an existing table. Or you might want to use SQL functions to pre-process the values from a given column (eg: to fomat a date). In this case, you can omit the `table` query string parameter, and instead provide a `query` parameter:

```
https://server.scraperwiki.com/box/publishtoken/cgi-bin/rss/feed.rss?query=SELECT+screen_name+AS+title,+profile_url+AS+link,+[…]+FROM+twitter_followers
```

The given SQL query must return five columns named `title`, `link`, `description`, `guid`, and `pubDate`. It should also include a `LIMIT` clause, to avoid server errors caused by extremely large result sets.

## Limitations

The RSS standard has no provision for auto-discovery of paginated feeds (unlike Atom, which supports `<link rel="next">`). Which means an RSS feed representing a database query must contain the entire query result in a single page.

For this reason, we provide you with a `limit` query string parameter, set to a default of 100 items. But be careful. Increasing the `limit` above this figure, or using a custom `query` without a SQL `LIMIT` clause, will result in increasingly slow HTTP responses, and eventually, 502 Gateway Timeout errors as the script is terminated for taking too long to request data from the database. So don’t even try it.

## Tests

Unit tests for the CGI script are stored in `/cgi-bin/rss`. You can run them with `nosetest` or `specloud`, like so:

```
cd tool/cgi-bin/rss
specloud
```

## Debugging 500 errors

The Python CGIHandler() we use often soaks up exceptions, making debugging 500 server errors particularly tricky. Try SSHing into your development dataset and running this, to see what's going wrong:

```
SERVER_NAME=premium.scraperwiki.com SERVER_PORT=80 REQUEST_METHOD=GET REQUEST_URI='/dqx2xyq/publishToken/cgi-bin/rss' PATH_INFO='/dqx2xyq/publishToken/cgi-bin/rss' tool/cgi-bin/rss/rss.py
```
