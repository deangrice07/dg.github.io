# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RACC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import os
import time
import requests
import peewee as pw
from requests.exceptions import RequestException
from Cryptodome.Cipher import AES
from hashlib import md5
from binascii import b2a_hex
from future.moves.urllib.parse import quote as orig_quote
from http.cookiejar import LWPCookieJar


def quote(s, safe=""):
    return orig_quote(s.encode("utf-8"), safe.encode("utf-8"))


db = pw.SqliteDatabase(None)


class BaseModel(pw.Model):
    class Meta:
        database = db


class Token(BaseModel):
    t_id = pw.IntegerField(unique=True)
    token_link = pw.TextField()


class Category(BaseModel):
    cid = pw.IntegerField(unique=True)
    category_name = pw.TextField()
    category_type = pw.TextField()
    category_image = pw.TextField()


class Channel(BaseModel):
    _id = pw.IntegerField(unique=True)
    cid = pw.IntegerField()
    title = pw.TextField()
    thumbnail = pw.TextField()
    updated = pw.FloatField(default=time.time)


class Stream(BaseModel):
    _id = pw.IntegerField(unique=True)
    channel_id = pw.ForeignKeyField(Channel, to_field="_id", backref="streams")
    name = pw.TextField()
    stream_url = pw.TextField()
    token = pw.ForeignKeyField(Token, to_field="t_id", backref="streams")
    agent = pw.TextField()
    referer = pw.TextField()


class Video(BaseModel):
    _id = pw.IntegerField(unique=True)
    cid = pw.IntegerField()
    title = pw.TextField()
    thumbnail = pw.TextField()
    updated = pw.FloatField(default=time.time)


class VodStream(BaseModel):
    _id = pw.IntegerField(unique=True)
    channel_id = pw.ForeignKeyField(Video, to_field="_id", backref="streams")
    name = pw.TextField()
    stream_url = pw.TextField()
    token = pw.ForeignKeyField(Token, to_field="t_id", backref="streams")
    agent = pw.TextField()
    referer = pw.TextField()


class SwiftStream:
    def __init__(self, cache_dir):
        DB = os.path.join(cache_dir, "swift0.db")
        COOKIE_FILE = os.path.join(cache_dir, "lwp_cookies.dat")
        db.init(DB)
        db.connect()
        db.create_tables([Token, Category, Channel, Stream, Video, VodStream], safe=True)
        self.base_url = "http://swiftstreamz.com/SwiftPanel/apiv1.php"
        self.user_agent = "okhttp/3.10.0"
        self.player_user_agent = "Lavf/56.15.102"
        self.s = requests.Session()
        self.s.cookies = LWPCookieJar(filename=COOKIE_FILE)
        if os.path.isfile(COOKIE_FILE):
            self.s.cookies.load(ignore_discard=True, ignore_expires=True)

    def __del__(self):
        db.close()
        self.s.cookies.save(ignore_discard=True, ignore_expires=True)
        self.s.close()

    def image_url(self, img):
        return "{0}|User-Agent={1}".format(img, quote(self.user_agent))

    @staticmethod
    def get_post_data():
        _key = b"cLt3Gp39O3yvW7Gw"
        _iv = b"bRRhl2H2j7yXmuk4"
        cipher = AES.new(_key, AES.MODE_CBC, iv=_iv)
        _time = str(int(time.time()))
        _hash = md5(
            "{0}e31Vga4MXIYss1I0jhtdKlkxxwv5N0CYSnCpQcRijIdSJYg".format(_time).encode("utf-8")
        ).hexdigest()
        _plain = "{0}&{1}".format(_time, _hash).ljust(48).encode("utf-8")
        cry = cipher.encrypt(_plain)
        return b2a_hex(cry).decode("utf-8")

    def api_request(self, url, params=None, data=None, json=True):
        headers = {"Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
        if data:
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
            req = requests.Request("POST", url, headers=headers, params=params, data=data)
        else:
            req = requests.Request("GET", url, headers=headers, params=params)
        prepped = self.s.prepare_request(req)
        del prepped.headers["User-Agent"]
        r = self.s.send(prepped, timeout=5)
        r.raise_for_status()
        if json:
            return r.json(strict=False)["LIVETV"]
        else:
            return r.text

    def update_tokens(self):
        tokens = []
        data = {"data": self.get_post_data()}
        for t in self.api_request(self.base_url, data=data)["token_list"]:
            tokens.append({"t_id": t.get("t_id"), "token_link": t.get("token_link")})
        with db.atomic():
            if len(tokens) > 2:
                """ Data fetch successful delete old data """
                Token.delete().execute()
            Token.replace_many(tokens).execute()

    def update_categories(self):
        self.update_tokens()
        categories = []
        for c in self.api_request(self.base_url, {"get_category": ""}):
            categories.append(
                {
                    "cid": c.get("cid"),
                    "category_name": c.get("category_name"),
                    "category_type": c.get("category_type"),
                    "category_image": self.image_url(c.get("category_image")),
                }
            )
        with db.atomic():
            if len(categories) > 2:
                """ Data fetch successful delete old data """
                Category.delete().execute()
            Category.replace_many(categories).execute()

    def update_category_videos(self, cid):
        _channels_by_cat_id = self.api_request(self.base_url, {"get_videos_by_cat_id": cid})
        videos = []
        streams = []
        for c in _channels_by_cat_id:
            videos.append(
                {
                    "_id": c.get("id"),
                    "cid": c.get("cid"),
                    "title": c.get("video_title"),
                    "thumbnail": self.image_url(c.get("video_thumbnail_b")),
                }
            )
            for s in c.get("stream_list"):
                streams.append(
                    {
                        "_id": s.get("vod_stream_id"),
                        "channel_id": c.get("id"),
                        "name": s.get("name"),
                        "stream_url": s.get("stream_url"),
                        "token": s.get("token"),
                        "agent": s.get("agent"),
                        "referer": s.get("referer_vod"),
                    }
                )
        with db.atomic():
            if len(streams) > 2:
                """ Data fetch successful delete old data """
                cat_channels = [v._id for v in Video.select().where(Video.cid == cid)]
                VodStream.delete().where(VodStream.channel_id.in_(cat_channels)).execute()
                Video.delete().where(Video.cid == cid).execute()
            for batch in pw.chunked(videos, 100):
                Video.replace_many(batch).execute()
            for batch in pw.chunked(streams, 100):
                VodStream.replace_many(batch).execute()

    def update_category_channels(self, cid):
        _channels_by_cat_id = self.api_request(self.base_url, {"get_channels_by_cat_id": cid})
        channels = []
        streams = []
        for c in _channels_by_cat_id:
            channels.append(
                {
                    "_id": c.get("id"),
                    "cid": c.get("cid"),
                    "title": c.get("channel_title"),
                    "thumbnail": self.image_url(c.get("channel_thumbnail")),
                }
            )
            for s in c.get("stream_list"):
                streams.append(
                    {
                        "_id": s.get("stream_id"),
                        "channel_id": c.get("id"),
                        "name": s.get("name"),
                        "stream_url": s.get("stream_url"),
                        "token": s.get("token"),
                        "agent": s.get("agent"),
                        "referer": s.get("referer"),
                    }
                )
        with db.atomic():
            if len(streams) > 2:
                """ Data fetch successful delete old data """
                cat_channels = [c._id for c in Channel.select().where(Channel.cid == cid)]
                Stream.delete().where(Stream.channel_id.in_(cat_channels)).execute()
                Channel.delete().where(Channel.cid == cid).execute()
            for batch in pw.chunked(channels, 100):
                Channel.replace_many(batch).execute()
            for batch in pw.chunked(streams, 100):
                Stream.replace_many(batch).execute()

    def get_categories(self):
        return Category.select().order_by(Category.category_type)

    def get_channels_by_category(self, cid, cache_time=0):
        channels = Channel.select().where(Channel.cid == cid)
        if channels.count() == 0:
            self.update_category_channels(cid)
        else:
            current_time = int(time.time())
            if current_time - int(channels[0].updated) > cache_time:
                try:
                    self.update_category_channels(cid)
                except (ValueError, RequestException):
                    pass
        """ !! select cursor reset in sqlite after update commit """
        return Channel.select().where(Channel.cid == cid)

    def get_videos_by_category(self, cid, cache_time=0):
        videos = Video.select().where(Video.cid == cid)
        if videos.count() == 0:
            self.update_category_videos(cid)
        else:
            current_time = int(time.time())
            if current_time - int(videos[0].updated) > cache_time:
                try:
                    self.update_category_videos(cid)
                except (ValueError, RequestException):
                    pass
        """ !! select cursor reset in sqlite after update commit """
        return Video.select().where(Video.cid == cid)

    def get_category(self, cid, cache_time=0):
        cat = Category.get(Category.cid == cid)
        if cat.category_type == "live":
            return self.get_channels_by_category(cid, cache_time)
        else:
            return self.get_videos_by_category(cid, cache_time)

    def get_channel_by_id(self, cid, _id, cache_time=0):
        cat = Category.get(Category.cid == cid)
        channels = self.get_category(cid, cache_time)
        if cat.category_type == "live":
            return Channel.get(Channel._id == _id)
        else:
            return Video.get(Video._id == _id)

    def get_stream_link(self, stream):
        data = {"data": self.get_post_data()}
        _token = self.api_request(stream.token.token_link, data=data, json=False).partition("=")[2]
        auth_token = "".join(
            [
                _token[:-59],
                _token[-58:-47],
                _token[-46:-35],
                _token[-34:-23],
                _token[-22:-11],
                _token[-10:],
            ]
        )
        return "{0}?wmsAuthSign={1}|User-Agent={2}&connection=keep-alive".format(
            stream.stream_url, auth_token, quote(self.player_user_agent)
        )
