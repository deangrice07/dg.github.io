# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-16-2019 by JewBMX in Scrubs.

import re
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils
from liptonscrapers.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['animexd.me']
        self.base_link = 'https://www.animexd.me'
        self.show_link = '/watch/%s_episode-%s-online'
        self.tv_maze = tvmaze.tvMaze()


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            tvshowtitle = self.tv_maze.showLookup('thetvdb', tvdb)
            url = tvshowtitle['name']
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            num = self.tv_maze.episodeAbsoluteNumber(tvdb, int(season), int(episode))
            url = self.base_link + self.show_link %(url.lower(), num)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            url = url.replace(' ','-')
            r = client.request(url, headers=client.randommobileagent('android'))
            match = re.compile("file: '(.+?)',", re.DOTALL).findall(r)
            for url in match:
                quality, info = source_utils.get_release_quality(url, url)
                sources.append({'source': 'Direct', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': True, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


