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
        self.domains = ['dl.my-film.me', 'dl.my-film.in', 'dl.my-film.info']
        self.base_link = 'http://dl.my-film.me/reza/film/'
        self.base_link1 = 'http://dl.my-film.me/s1/Movie/'
        self.base_link2 = 'http://dl.my-film.me/Movie/2160p.4K/'
        self.base_link3 = 'http://dl.my-film.me/Movie/BluRay%20720p/'
        self.base_link4 = 'http://dl.my-film.me/Movie/BluRay%20720p-x265/'
        self.base_link5 = 'http://dl.my-film.me/Movie/BluRay1080p/'
        self.base_link6 = 'http://dl.my-film.me/Movie/BluRay1080p-x265/'
        self.base_link7 = 'http://dl.my-film.me/Movie/DVDrip/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.get_query(title)
            self.title = '%s.%s' % (title, year)
            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            try:
                url = self.base_link
                r = requests.get(url, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    url = self.base_link + url
                    quality = source_utils.check_direct_url(url)
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                url = self.base_link1
                r = requests.get(url, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for u in r:
                    if not self.title in u: continue
                    t = self.base_link1 + u
                    i = requests.get(t, timeout=10).content
                    i = re.compile('a href="(.+?)"').findall(i)
                    for url in i:
                        if 'DUBLE' in url: continue
                        url = t + url
                        quality = source_utils.check_direct_url(url)
                        sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link2
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    quality = source_utils.check_direct_url(url)
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link3
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    sources.append({'source': 'DL', 'quality': '720p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link4
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    sources.append({'source': 'DL', 'quality': '720p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link5
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    sources.append({'source': 'DL', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link6
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    sources.append({'source': 'DL', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                result = self.base_link7
                r = requests.get(result, timeout=10).content
                r = re.compile('a href="(.+?)"').findall(r)
                for url in r:
                    if not self.title in url: continue
                    if any(x in url for x in ['Dubbed']): continue
                    url = result + url
                    quality = source_utils.check_direct_url(url)
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            except:
                return
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
