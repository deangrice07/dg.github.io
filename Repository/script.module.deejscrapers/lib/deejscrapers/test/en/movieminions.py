# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re, requests

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils
from liptonscrapers.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movieminions.net']
        self.base_link = 'https://movieminions.net/english-movies/movies'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.get_query(title)
            title = '%s.%s' % (title, year)
            self.title = title.replace('-', '.')
            year = '-%s/' % year
            url = self.base_link + year
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            result = url
            try:
                r = requests.get(result, timeout=10).content
                r = client.parseDOM(r, "table", attrs={"id": "list"})
                for r in r:
                    r = re.compile('a title=".+?" data-xyz="(.+?)"').findall(r)
                    for url in r:
                        if not self.title in url: continue
                        url = 'http://' + url
                        quality = source_utils.check_url(url)
                        sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
            except:
                return
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
