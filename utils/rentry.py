#!/usr/bin/env python3

# @source: https://github.com/radude/rentry/blob/master/rentry.py

import http.cookiejar
import urllib.parse
import urllib.request
from http.cookies import SimpleCookie
from json import loads as json_loads

BASE_PROTOCOL="https://"
BASE_URL="rentry.co"

_headers = {"Referer": f"{BASE_PROTOCOL}{BASE_URL}"}


class UrllibClient:
    """Simple HTTP Session Client, keeps cookies."""

    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        urllib.request.install_opener(self.opener)

    def get(self, url, headers={}):
        request = urllib.request.Request(url, headers=headers)
        return self._request(request)

    def post(self, url, data=None, headers={}):
        postdata = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(url, postdata, headers)
        return self._request(request)

    def _request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read().decode('utf-8')
        return response


def raw(url):
    client = UrllibClient()
    return json_loads(client.get(f"{BASE_PROTOCOL}{BASE_URL}" + '/api/raw/{}'.format(url)).data)


def new(url, edit_code, text):
    client, cookie = UrllibClient(), SimpleCookie()

    cookie.load(vars(client.get(f"{BASE_PROTOCOL}{BASE_URL}"))['headers']['Set-Cookie'])
    csrftoken = cookie['csrftoken'].value

    payload = {
        'csrfmiddlewaretoken': csrftoken,
        'url': url,
        'edit_code': edit_code,
        'text': text
    }

    return json_loads(client.post(f"{BASE_PROTOCOL}{BASE_URL}" + '/api/new', payload, headers=_headers).data)


def edit(url, edit_code, text):
    client, cookie = UrllibClient(), SimpleCookie()

    cookie.load(vars(client.get(f"{BASE_PROTOCOL}{BASE_URL}"))['headers']['Set-Cookie'])
    csrftoken = cookie['csrftoken'].value

    payload = {
        'csrfmiddlewaretoken': csrftoken,
        'edit_code': edit_code,
        'text': text
    }

    return json_loads(client.post(f"{BASE_PROTOCOL}{BASE_URL}" + '/api/edit/{}'.format(url), payload, headers=_headers).data)
