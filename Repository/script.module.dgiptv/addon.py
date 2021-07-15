# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 - 2019 RACC
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

import sys
from xbmcgui import ListItem
from kodi_six import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from routing import Plugin

import os
import time
from requests.exceptions import RequestException
from resources.lib.swift import SwiftStream

addon = xbmcaddon.Addon()
plugin = Plugin()
plugin.name = addon.getAddonInfo("name")
USER_DATA_DIR = xbmc.translatePath(addon.getAddonInfo("profile"))
data_time = int(addon.getSetting("data_time") or "0")
cache_time = int(addon.getSetting("cache_time") or "0") * 60 * 60
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)


def log(msg, level=xbmc.LOGNOTICE):
    xbmc.log("[{0}] {1}".format(plugin.name, msg), level=level)


TV = SwiftStream(USER_DATA_DIR)
current_time = int(time.time())
if current_time - data_time > cache_time:
    try:
        TV.update_categories()
        addon.setSetting("data_time", str(current_time))
        log("[{0}] Categories updated".format(current_time))
    except (ValueError, RequestException) as e:
        if data_time == 0:
            """ No data """
            dialog = xbmcgui.Dialog()
            dialog.notification(plugin.name, e.message, xbmcgui.NOTIFICATION_ERROR)
            xbmcplugin.endOfDirectory(plugin.handle, False)
        else:
            """ Data update failed """
            log("[{0}] Categories update fail, data age: {1}".format(current_time, data_time))
            log(e.message)


@plugin.route("/")
def root():
    list_items = []
    for cat in TV.get_categories():
        li = ListItem(cat.category_name, offscreen=True)
        li.setArt({"thumb": cat.category_image, "icon": cat.category_image})
        url = plugin.url_for(list_channels, cat_id=cat.cid)
        list_items.append((url, li, True))
    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_channels/<cat_id>")
def list_channels(cat_id):
    list_items = []
    try:
        for channel in TV.get_category(cat_id, cache_time):
            title = channel.title
            image = channel.thumbnail
            li = ListItem(title, offscreen=True)
            li.setProperty("IsPlayable", "true")
            li.setArt({"thumb": image, "icon": image})
            li.setInfo(type="Video", infoLabels={"Title": title, "mediatype": "video"})
            li.setContentLookup(False)
            url = plugin.url_for(play, cat_id=channel.cid, channel_id=channel._id)
            list_items.append((url, li, False))
        xbmcplugin.addDirectoryItems(plugin.handle, list_items)
        xbmcplugin.endOfDirectory(plugin.handle)
    except (ValueError, RequestException) as e:
        """ No data """
        log(e.message)
        dialog = xbmcgui.Dialog()
        dialog.notification(plugin.name, e.message, xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.endOfDirectory(plugin.handle, False)


@plugin.route("/play/<cat_id>/<channel_id>/play.pvr")
def play(cat_id, channel_id):
    channel = TV.get_channel_by_id(cat_id, channel_id, cache_time)
    title = channel.title
    image = channel.thumbnail
    try:
        if len(channel.streams) > 1:
            dialog = xbmcgui.Dialog()
            ret = dialog.select("Choose Stream", [s.name for s in channel.streams])
            stream = channel.streams[ret]
        else:
            stream = channel.streams[0]
        media_url = TV.get_stream_link(stream)
        li = ListItem(title, path=media_url, offscreen=True)
        if "playlist.m3u8" in media_url:
            if addon.getSetting("inputstream") == "true":
                li.setMimeType("application/vnd.apple.mpegurl")
                li.setProperty("inputstreamaddon", "inputstream.adaptive")
                li.setProperty("inputstream.adaptive.manifest_type", "hls")
                li.setProperty("inputstream.adaptive.stream_headers", media_url.split("|")[-1])
            else:
                li.setMimeType("application/vnd.apple.mpegurl")
        else:
            li.setMimeType("video/x-mpegts")
        li.setArt({"thumb": image, "icon": image})
        li.setContentLookup(False)
        xbmcplugin.setResolvedUrl(plugin.handle, True, li)
    except (ValueError, RequestException) as e:
        log(e.message)
        dialog = xbmcgui.Dialog()
        dialog.notification(plugin.name, e.message, xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.setResolvedUrl(plugin.handle, False, ListItem())


if __name__ == "__main__":
    plugin.run(sys.argv)
    del TV
