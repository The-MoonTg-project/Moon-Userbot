#!/usr/bin/env python3

# @source: https://github.com/radude/rentry/blob/master/rentry.py
import asyncio
import http.cookiejar
import urllib.parse
import urllib.request

from uuid import uuid4
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from json import loads as json_loads

from utils.db import db

BASE_PROTOCOL = "https://"
BASE_URL = "rentry.co"

_headers = {"Referer": f"{BASE_PROTOCOL}{BASE_URL}"}


class UrllibClient:
    """Simple HTTP Session Client, keeps cookies."""

    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        urllib.request.install_opener(self.opener)

    def get(self, url, headers=None):
        if headers is None:
            headers = {}
        request = urllib.request.Request(url, headers=headers)
        return self._request(request)

    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        postdata = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(url, postdata, headers)
        return self._request(request)

    def _request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read().decode("utf-8")
        return response


def raw(url: str):
    client = UrllibClient()
    return json_loads(client.get(f"{BASE_PROTOCOL}{BASE_URL}/api/raw/{url}").data)


def new(text: str, edit_code: str = "", url: str = ""):
    client, cookie = UrllibClient(), SimpleCookie()

    cookie.load(vars(client.get(f"{BASE_PROTOCOL}{BASE_URL}"))["headers"]["Set-Cookie"])
    csrftoken = cookie["csrftoken"].value

    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "url": url,
        "edit_code": edit_code,
        "text": text,
    }

    return json_loads(
        client.post(
            f"{BASE_PROTOCOL}{BASE_URL}" + "/api/new", payload, headers=_headers
        ).data
    )


def edit(url_short: str, edit_code: str, text: str):
    client, cookie = UrllibClient(), SimpleCookie()

    cookie.load(vars(client.get(f"{BASE_PROTOCOL}{BASE_URL}"))["headers"]["Set-Cookie"])
    csrftoken = cookie["csrftoken"].value

    payload = {"csrfmiddlewaretoken": csrftoken, "edit_code": edit_code, "text": text}

    return json_loads(
        client.post(
            f"{BASE_PROTOCOL}{BASE_URL}/api/edit/{url_short}", payload, headers=_headers
        ).data
    )


def delete(url_short: str, edit_code: str):
    client, cookie = UrllibClient(), SimpleCookie()
    cookie.load(vars(client.get(f"{BASE_PROTOCOL}{BASE_URL}"))["headers"]["Set-Cookie"])
    csrftoken = cookie["csrftoken"].value
    payload = {"csrfmiddlewaretoken": csrftoken, "edit_code": edit_code}
    return json_loads(
        client.post(
            f"{BASE_PROTOCOL}{BASE_URL}/api/delete/{url_short}",
            payload,
            headers=_headers,
        ).data
    )


async def paste(
    text: str,
    return_edit: bool = False,
    edit_bin: bool = False,
    edit_code: str = None,
    url: str = None,
    permanent: bool = False,
) -> str | tuple[str, str]:
    """Pastes some text to rentry bin.
    args:
        text: Input text to paste
        return_edit: If it should return edit code also
        edit_bin: If this request is to edit an already existing bin
        edit_code: Only required if edit_bin is True. It is the edit code used to edit bin.
        url: Only required if edit_bin is True. It is the url on which the bin is located.
        permanent: If the pasted content should not be deleted automatically

    returns:
        The url of the paste or return a tuple containing url and edit code
    """
    if not str(text):
        return

    if edit_bin:
        if not (url and edit_code):
            raise ValueError("Please provide both, url and edit code")
        response = edit(url_short=url, edit_code=edit_code, text=text)
    else:
        response = new(text=text)

    if response.get("status") != "200":
        raise RuntimeError(
            f"paste task terminated with status: {response.get('status')}\n"
            f"Message: {response.get('content', 'No message provided')}"
        )

    url = response["url"]
    edit_code = response["edit_code"]

    if not permanent:
        short_url = response["url_short"]
        time_now = datetime.now()
        ftime = time_now.strftime("%d %I:%M:%S %p %Y")

        print(f"URL: {url} - Edit Code: {edit_code} - Time: {ftime}")

        rallUrls = db.get("core.rentry", "urls", default={"allUrls": {}})
        entry_id = str(uuid4())
        rallUrls["allUrls"][entry_id] = {
            "url": short_url,
            "edit_code": edit_code,
            "time": ftime,
        }
        db.set("core.rentry", "urls", rallUrls)

    if return_edit:
        return (url, edit_code)
    return url


async def rentry_cleanup_job():
    """Periodically checks and deletes rentry pastes older than 24 hours"""
    while True:
        try:
            rallUrls = db.get("core.rentry", "urls", default={"allUrls": {}})
            now = datetime.now()
            deleted_count = 0
            error_count = 0

            for entry_id, entry in list(rallUrls["allUrls"].items()):
                url = entry["url"]
                entry_time = datetime.strptime(entry["time"], "%d %I:%M:%S %p %Y")

                if now - entry_time > timedelta(days=1):
                    try:
                        delete(url, entry["edit_code"])
                        del rallUrls["allUrls"][entry_id]
                        deleted_count += 1
                        print(f"[#] Deleted expired rentry paste: {url}")
                    except Exception as e:
                        error_count += 1
                        print(f"[!] Failed to delete rentry paste {url}: {str(e)}")

            if deleted_count or error_count:
                print(
                    f"[*] Cleanup summary: {deleted_count} deleted, {error_count} failed"
                )

            if deleted_count:
                db.set("core.rentry", "urls", rallUrls)

        except Exception as e:
            print(f"[!] Error in rentry cleanup job: {str(e)}")

        await asyncio.sleep(12 * 60 * 60)
