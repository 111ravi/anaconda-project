from __future__ import absolute_import, print_function

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


@gen.coroutine
def _http_fetch(request, host=None):
    http_client = AsyncHTTPClient()
    headers = dict()
    if host is not None:
        headers['Host'] = host
    response = yield http_client.fetch(request, headers=headers)

    if response.error:
        raise response.error
    else:
        raise gen.Return(response)


def http_get_async(url, host=None):
    return _http_fetch(HTTPRequest(url=url, method='GET'), host=host)


def http_post_async(url, body=None, host=None, headers=None):
    return _http_fetch(HTTPRequest(url=url, method='POST', body=body, headers=headers), host=host)


def http_get(io_loop, url, host=None):
    return io_loop.run_sync(lambda: http_get_async(url, host))


def http_post(io_loop, url, body=None, host=None, headers=None):
    return io_loop.run_sync(lambda: http_post_async(url, body, host, headers))
