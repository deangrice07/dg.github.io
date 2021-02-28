# -*- coding: utf-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
#  As long as you retain this notice you can do whatever you want with this
# stuff. Just please ask before copying. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Atreides
# Addon id: plugin.video.atreides
# Addon Provider: House Atreides

import os
import re
import sys
import traceback
import urllib
import urlparse

import xbmcgui
import xbmcplugin
from resources.lib.modules import client, control, jsonbm, jsonmenu, log_utils

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
artPath = control.artPath()
addonFanart = control.addonFanart()


class podcast:
    def __init__(self):
        self.list = []

        self.pco_link = 'https://www.podcastone.com'
        self.pco_page_link = 'https://www.podcastone.com/pg/jsp/program/pasteps_cms.jsp?size=15&amountToDisplay=15&page=%s&infiniteScroll=true&progID=%s&showTwitter=true&pmProtect=false&displayPremiumEpisodes=false&startAt=0'
        self.pco_play_link = 'https://www.podcastone.com/downloadsecurity?url=%s'
        self.pcocats_link = 'https://www.podcastone.com/%s'
        self.pb_link = 'http://podbay.fm/'
        self.pbcats_link = 'http://podbay.fm/browse/%s'

    def root(self):
        rootMenu = jsonmenu.jsonMenu()
        rootMenu.load('podcast')
        rootMenu.process('podcast_root')
        self.endDirectory(category='Podcasts')

    def pco_root(self):
        rootMenu = jsonmenu.jsonMenu()
        rootMenu.load('podcast')
        rootMenu.process('podcastone_root')
        self.endDirectory(category='PodcastOne')

    def pb_root(self):
        rootMenu = jsonmenu.jsonMenu()
        rootMenu.load('podcast')
        rootMenu.process('podbay_root')
        self.endDirectory(category='Podbay.fm')

    def pco_cat(self, category):
        try:
            items = []
            url = self.pcocats_link % category
            html = client.request(url)

            div_list = re.compile(
                '<div class="podcast-container flex no-wrap" data-program-name="(.+?)">(.+?)</a></div>',
                re.DOTALL).findall(html)
            for show_title, content in div_list:
                show_url = re.compile('href="(.+?)"', re.DOTALL).findall(content)[0]
                show_url = show_url.replace('/', '', 1)
                if 'viewProgram' in show_url:
                    url = self.pcocats_link % show_url
                    html = client.request(url)
                    more_ep_block = re.compile('<div class="col-xs-12">(.+?)</div>', re.DOTALL).findall(html)[0]
                    show_url = re.compile(
                        'href="(.+?)"', re.DOTALL).findall(more_ep_block)[0].replace('/', '').replace('?showAllEpisodes=true', '')
                icon = urlparse.urljoin(self.pco_link, re.compile('<img src="(.+?)"', re.DOTALL).findall(content)[0])
                show_action = 'podcastOne&podcastshow=%s&page=1' % show_url

                item = control.item(label=show_title)
                item.setArt({"thumb": icon, "icon": icon})
                item.setProperty("IsPlayable", "false")
                link = '%s?action=%s' % (sysaddon, show_action)

                '''
                Let's build out this context menu bitches
                '''
                try:
                    cm = jsonbm.jsonBookmarks().build_cm('Podcasts', name=show_title, id=show_url, action='podcastOne', icon=icon, url=show_url+'&page=1')
                    if len(cm) > 0:
                        item.addContextMenuItems(cm)
                except Exception:
                    failure = traceback.format_exc()
                    log_utils.log('PodcastOne - BM Exception: \n' + str(failure))

                items.append((link, item, True))
        except Exception:
            pass

        control.addItems(syshandle, items)
        self.endDirectory()
        return

    def pb_cat(self, category):
        try:
            items = []
            url = self.pbcats_link % category
            html = client.request(url)

            page_list = re.compile('<ul class="thumbnails">(.+?)</ul>', re.DOTALL).findall(html)[0]
            show_list = re.compile('<li class="span3">(.+?)</li>', re.DOTALL).findall(page_list)
            for entry in show_list:
                show_url = re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
                icon = re.compile('src="(.+?)"', re.DOTALL).findall(entry)[0]
                show_title = re.compile('<h4>(.+?)</h4>', re.DOTALL).findall(entry)[0].encode('utf-8', 'ignore').decode('utf-8')
                show_action = 'podbay&podcastshow=%s' % show_url
                link = '%s?action=%s' % (sysaddon, show_action)

                item = control.item(label=show_title)
                item.setArt({"thumb": icon, "icon": icon})
                item.setProperty("IsPlayable", "false")

                '''
                Let's build out this context menu bitches
                '''
                try:
                    cm = jsonbm.jsonBookmarks().build_cm('Podcasts', name=show_title, id=show_url, action='podbay', icon=icon, url=show_url)
                    if len(cm) > 0:
                        item.addContextMenuItems(cm)
                except Exception:
                    failure = traceback.format_exc()
                    log_utils.log('Podbay - BM Exception: \n' + str(failure))

                items.append((link, item, True))
        except Exception:
            pass

        control.addItems(syshandle, items)
        self.endDirectory()
        return

    def pco_show(self, show, page):
        try:
            url = self.pcocats_link % show
            url = url + '?showAllEpisodes=true'
            html = client.request(url)
            progID = re.compile('categoryID2=(.+?)"', re.DOTALL).findall(html)[0]

            first = None
            items = []
            if page == '1':
                icon_item = client.parseDOM(html, 'div', attrs={'class': 'col-sm-3 col-xs-12 current-episode-img'})[0]
                icon = client.parseDOM(icon_item, 'img', ret='src')[0]

                latest_content = re.compile('<div class="letestEpiDes">(.+?)</div>', re.DOTALL).findall(html)[0]
                ep_title = re.compile('href=".+?" style="color:inherit;">(.+?)</a>', re.DOTALL).findall(latest_content)[0]
                first = ep_title
                ep_page = urlparse.urljoin(self.pco_link, re.compile('href="(.+?)"', re.DOTALL).findall(latest_content)[0])
                episode_action = 'podcastOne&podcastepisode=%s' % ep_page

                item = control.item(label=ep_title)
                item.setArt({"thumb": icon, "icon": icon})
                item.setInfo(type="music", infoLabels={"Title": ep_title, "mediatype": "music"})
                item.setProperty("IsPlayable", "true")
                link = '%s?action=%s' % (sysaddon, episode_action)
                items.append((link, item, False))

            url = self.pco_page_link % (page, progID)
            html = client.request(url)

            episode_list = client.parseDOM(html, 'div', attrs={'class': 'flex space-between align-center no-wrap'})
            for content in episode_list:
                icon = re.compile('src="(.+?)"', re.DOTALL).findall(content)[0]
                ep_title = re.compile('href=".+?" style="color:inherit;">(.+?)</a>', re.DOTALL).findall(content)[0]
                if ep_title == first:
                    continue
                ep_page = urlparse.urljoin(self.pco_link, re.compile('href="(.+?)"', re.DOTALL).findall(content)[0])
                episode_action = 'podcastOne&podcastepisode=%s' % ep_page

                item = control.item(label=ep_title)
                item.setArt({"thumb": icon, "icon": icon})
                item.setInfo(type="music", infoLabels={"Title": ep_title, "mediatype": "music"})
                item.setProperty("IsPlayable", "true")
                link = '%s?action=%s' % (sysaddon, episode_action)
                items.append((link, item, False))
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('PodCastOne Show - Exception: \n' + str(failure))

        try:
            if len(items) > 13:
                next_url = '%s?action=podcastOne&podcastshow=%s&page=%s' % (sysaddon, show, int(page)+1)
                item = control.item(label=control.lang(32053).encode('utf-8'))
                item.setArt({"thumb": control.addonNext(), "icon": control.addonNext()})
                items.append((next_url, item, True))
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('PodCastOne Show - Exception: \n' + str(failure))

        control.addItems(syshandle, items)
        self.endDirectory()
        return

    def pb_show(self, show):
        try:
            url = urlparse.urljoin(self.pb_link, show)
            html = client.request(url)

            show_icon = re.compile('<meta property="og:image" content="(.+?)"').findall(html)[0]
            table_content = client.parseDOM(html, 'div', attrs={'class': 'span8 well'})[0]
            table_rows = client.parseDOM(table_content, 'tr')
            for row in table_rows:
                if '<th' in row:
                    continue
                row = ''.join(row.splitlines())
                if 'href' in row:
                    ep_page = re.compile('href="(.+?)"').findall(row)[0].replace('?autostart=1', '')
                else:
                    continue
                ep_title = re.compile('<a\s.*?>(.+?)</a>').findall(row)[0].encode('utf-8', 'ignore').decode('utf-8')
                episode_action = 'podbay&podcastepisode=%s' % ep_page
                self.list.append({'name': ep_title, 'url': ep_page, 'image': show_icon, 'action': episode_action})
            self.addDirectory(self.list, False, False)
            return self.list
        except Exception as e:
            log_utils.log('Exception - ' + str(e))
            pass

    def podcast_play(self, action, url):
        try:
            if 'podcastOne' in action:
                ep_page = client.request(url)
                episode_item = client.parseDOM(ep_page, 'div', attrs={'class': 'media-player'})[0]
                episode_item2 = client.parseDOM(ep_page, 'div', attrs={'class': 'letestepi'})[0]
                ep_icon = client.parseDOM(episode_item2, 'img', attrs={'class': 'img-responsive'}, ret='src')[0]
                ep_title = client.parseDOM(ep_page, 'title')[0].replace('PodcastOne: ', '')
                play_url = re.compile(
                    'href="(.+?)"', re.DOTALL).findall(episode_item)[0].replace("\n", "").replace('/downloadsecurity?url=', '')
                url = self.pco_play_link % play_url
            elif 'podbay' in action:
                ep_page = client.request(url)
                ep_icon = client.parseDOM(ep_page, 'meta', attrs={'property': 'og:image'}, ret='content')[0]
                ep_title = client.parseDOM(
                    ep_page, 'meta', attrs={'property': 'og:title'},
                    ret='content')[0].encode(
                    'utf-8', 'ignore').decode('utf-8')
                url = client.parseDOM(ep_page, 'a', attrs={'class': 'btn btn-mini btn-primary'}, ret='href')[0]
            item = control.item(label=ep_title, path=url, iconImage=ep_icon, thumbnailImage=ep_icon)
            item.setInfo(type="audio", infoLabels={"title": ep_title})
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        except Exception as e:
            log_utils.log('podcast_play:Exception - ' + str(e))
            pass

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        try:
            name = control.lang(name).encode('utf-8')
        except Exception:
            pass
        url = '%s?action=%s' % (sysaddon, query) if isAction is True else query
        if 'http' not in thumb:
            thumb = os.path.join(artPath, thumb) if artPath is not None else icon
        cm = []

        queueMenu = control.lang(32065).encode('utf-8')

        if queue is True:
            cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if context is not None:
            cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb})
        if addonFanart is not None:
            item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, contentType='addons', sortMethod=control.xDirSort.NoSort, category=None):
        control.content(syshandle, contentType)
        if category is not None:
            control.category(syshandle, category)
        if sortMethod is not control.xDirSort.NoSort:
            control.sortMethod(syshandle, sortMethod)
        control.directory(syshandle, cacheToDisc=True)

    def addDirectory(self, items, queue=False, isFolder=True):
        if items is None or len(items) == 0:
            control.idle()
            sys.exit()

        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'):
                    thumb = i['image']
                elif artPath is not None:
                    thumb = os.path.join(artPath, i['image'])
                else:
                    thumb = addonThumb

                item = control.item(label=name)

                if isFolder:
                    url = '%s?action=%s' % (sysaddon, i['action'])
                    try:
                        url += '&url=%s' % urllib.quote_plus(i['url'])
                    except Exception:
                        pass
                    item.setProperty('IsPlayable', 'false')
                else:
                    url = '%s?action=%s' % (sysaddon, i['action'])
                    try:
                        url += '&url=%s' % i['url']
                    except Exception:
                        pass
                    item.setProperty('IsPlayable', 'true')
                    item.setInfo("mediatype", "video")
                    item.setInfo("audio", '')

                item.setArt({'icon': thumb, 'thumb': thumb})
                if addonFanart is not None:
                    item.setProperty('Fanart_Image', addonFanart)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except Exception:
                pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)
