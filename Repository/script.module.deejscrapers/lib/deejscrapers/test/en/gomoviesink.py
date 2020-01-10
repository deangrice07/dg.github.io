# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils
from liptonscrapers.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.gomovies.ink/gomovies']
        self.base_link = 'www.gomovies.ink/gomovies'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('-', '+')
            u = self.base_link + self.search_link % title
            u = self.scraper.get(u).content
            i = client.parseDOM(u, "div", attrs={"class": "movies-list movies-list-full"})
            for r in i:
                r = re.compile('<a href="(.+?)"').findall(r)
                for url in r:
                    title = cleantitle.geturl(title)
                    if title not in url:
                        continue
                    return url
        except:
            return url

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            r = self.scraper.get(url).content
            qual = re.compile('class="quality">(.+?)<').findall(r)
            for i in qual:
                if 'HD' in i:
                    quality = '720p'
                else:
                    quality = 'SD'
            r = client.parseDOM(r, "div", attrs={"id": "mv-info"})
            for i in r:
                t = re.compile('<a href="(.+?)"').findall(i)
                for url in t:
                    t = self.scraper.get(url).content
                    t = client.parseDOM(t, "div", attrs={"id": "content-embed"})
                    for u in t:
                        i = re.findall('iframe src="(.+?)"', u)
                        for url in i:
                            valid, host = source_utils.is_host_valid(url, hostDict)
                            if valid:
                                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
