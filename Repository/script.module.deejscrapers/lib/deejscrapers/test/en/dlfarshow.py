# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re, requests

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['dl.farshow.ir']
        self.base_link = 'http://dl.farshow.ir/Series/Foreign/'
        self.search_link = '%s/'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            title = cleantitle.get_query(tvshowtitle)
            title = '%s' % title
            url = self.base_link + self.search_link % title
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            self.se = 'S%02dE%02d' % (int(season), int(episode))
            season = 'S%02d/' % int(season)
            if not url: return
            url = url + season
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            se = self.se
            result = url
            r = requests.get(result, timeout=10).content
            r = re.findall('a href=".+?">(.+?)<', r)
            for r in r:
                if '1080p/' in r:
                    result2 = result + '1080p/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif '1080p.10bit.x265/' in r:
                    result2 = result + '1080p.10bit.x265/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif '1080p.x265/' in r:
                    result2 = result + '1080p.x265/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif '720p.x265/' in r:
                    result2 = result + '720p.x265/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '720p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif '720p/' in r:
                    result2 = result + '720p/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '720', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif '480p/' in r:
                    result2 = result + '480p/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '480p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif 'Org/' in r:
                    result2 = result + 'Org/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        url = result2 + url
                        sources.append({'source': 'DL', 'quality': '480p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                elif 'Double/' in r:
                    result2 = result + 'Double/'
                    r = requests.get(result2, timeout=10).content
                    r = re.findall('a href=".+?">(.+?)<', r)
                    for url in r:
                        if not se in url: continue
                        if any(x in url for x in ['Dubbed']): raise Exception()
                        url = result2 + url
                        quality = source_utils.check_direct_url(url)
                        sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                else:
                    if not se in r: continue
                    url = result + r
                    quality = source_utils.check_direct_url(url)
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
