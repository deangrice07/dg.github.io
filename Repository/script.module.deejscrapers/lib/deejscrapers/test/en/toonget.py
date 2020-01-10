# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
from liptonscrapers.modules import client
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_tools


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['toonget.net']
        self.base_link = 'https://toonget.net'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = '%s-%s' % (title, year)
            url = self.base_link + '/' + url
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            if season == '1': 
                url = self.base_link + '/' + url + '-episode-' + episode
            else:
                url = self.base_link + '/' + url + '-season-' + season + '-episode-' + episode
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            r = client.request(url)
            match = re.compile('<iframe src="(.+?)"').findall(r)
            for url in match:
                r = client.request(url)
                if 'playpanda' in url:
                    match = re.compile("url: '(.+?)',").findall(r)
                else:
                    match = re.compile('file: "(.+?)",').findall(r)
                for url in match:
                    url = url.replace('\\','')
                    if url in str(sources):
                        continue
                    info = source_tools.get_info(url)
                    quality = source_tools.get_quality(url)
                    sources.append({'source': 'Direct', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


