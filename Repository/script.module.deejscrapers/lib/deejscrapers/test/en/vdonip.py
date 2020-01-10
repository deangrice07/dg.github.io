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
        self.domains = ['vdonip.com']
        self.base_link = 'http://vdonip.com'
        self.search_link = '/English/%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.get_query(title)
            title = '%s' % title
            url = self.base_link + self.search_link % year
            r = requests.get(url).content
            r = re.compile('a href="(.+?)"').findall(r)
            for u in r:
                if not title in u:
                    continue
                url = self.base_link + u
                i = requests.get(url).content
                i = re.compile('a href="(.+?)"').findall(i)
                for t in i:
                    if not title in t:
                        continue
                    if '.srt' in t:
                        continue
                    url = self.base_link + t
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            quality = source_utils.check_url(url)
            sources.append({'source': 'Direct', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            return sources
        except:
            return

    def resolve(self, url):
        return url
