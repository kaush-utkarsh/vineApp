# coding: utf-8

import json
import logging
import requests
from utils import *
import ConfigParser
from flask import  session
from config import *

class VineError(Exception):
    def __init__(self, response):
        self.code = response["code"]
        self.message = response["error"]

    def __str__(self):
        return str(self.message)

class Vine(object):
    def __init__(self):
        self._user_id = None
        self._key = None
        self.date_fmt = '%Y-%m-%dT%H:%M:%S.%f'

    def login(self, username, password):
        response = self._call("users/authenticate", data={"username": username, "password": password})
        self._user_id = response["data"]["userId"]
        self._key = response["data"]["key"]

    def tag(self, tag_, page=None, size=None):
        return self._call("timelines/tags/%s" % tag_, params={"page": page, "size": size})["data"]

    def popular(self, page=None, size=None):
        return self._call("timelines/popular", params={"page": page, "size": size})["data"]

    def venues(self, venue_id_, page=None, size=None):
        return self._call("timelines/venues/%s" % venue_id_, params={"page": page, "size": size})["data"]

    def search_user(self, username_, page=None, size=None):
        return self._call("users/search/%s" % username_, params={"page": page, "size": size})["data"]

    def search_tag(self, tag_, page=None, size=None):
        return self._call("timelines/tags/%s" % tag_, params={"page": page, "size": size})["data"]
        # return self._call("tags/search/%s" % tag_, params={"page": page, "size": size})["data"]

    def search(self, tag, page=1, media_list=[]):
        vt = self.search_tag(tag, page)
        if vt["count"] > 0:
            for v in vt.get("records"):
                if v.get("videoUrl"):
                    media = {}
                    media["serial_no"] = len(media_list) + 1
                    media["tag_url"] = v.get("videoUrl")
                    media["full_name"] = "%s(%d)" % (v.get("username"), v.get("userId"))
                    media["profile_picture"] = v.get("avatarUrl")
                    media["created_time"] = (differenceBetweenDates(v.get("created"), self.date_fmt) + " ago, <br>" + convertToPTTimezone(v.get("created"), self.date_fmt).strftime('%H:%M:%S %b %d %Y')).replace("-", "")
                    media["text"] = v.get("description")
                    media["tag"] = tag
                    media["id"] = v.get("postId")
                    media_list.append(media)

        session['nextPage'] = vt.get("nextPage")
        print session['nextPage']
        if len(media_list) < VIDEOS_LIMIT and vt.get("nextPage", 0) > 0:
            self.search(tag, vt.get("nextPage"), media_list)

        return json.dumps(media_list[0:VIDEOS_LIMIT])

    def _call(self, call, params=None, data=None):
        """Make an API call. Return the parsed response. If login has
        been called, make an authenticated call. If data is not None,
        it's a post request.
        """
        url = VINE_API_BASE_URL + call
        headers = {"User-Agent": "com.vine.iphone/1.0.3 (unknown, iPhone OS 6.0.1, iPhone, Scale/2.000000)",
                   "Accept-Language": "en, en-us;q=0.8"}
        if self._key:
            headers["vine-session-id"] = self._key

        if data:
            r = requests.post(url, params=params, data=data, headers=headers, verify=False)
        else:
            r = requests.get(url, params=params, headers=headers, verify=False)

        try:
            # print r.text
            data = r.json()
            if data.get("success") is not True:
                raise VineError(data)
            return data
        except:
            logging.error(r.text)
            raise