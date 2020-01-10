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
        self.domains = ['ww.lalbatte.net']
        self.base_link = 'http://ww.lalbatte.net/movies/English/'
        self.search_link = '%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.get_query(title)
            self.title = '%s.%s' % (title, year)
            self.year = year
            url = self.base_link + self.search_link % self.year
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = requests.get(url, timeout=10).content
            r = re.compile('a href="(.+?)"').findall(r)
            for url in r:
                if not self.title in url:
                    continue
                if any(x in url for x in ['Trailer', 'Dubbed']): continue
                url = self.base_link + self.search_link % self.year + url
                quality = source_utils.check_url(url)
                sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            return sources
        except:
            return

    def resolve(self, url):
        return url
