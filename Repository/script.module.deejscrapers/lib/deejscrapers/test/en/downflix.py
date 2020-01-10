# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
import traceback

from liptonscrapers.modules import cfscrape, cleantitle, directstream, log_utils, source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['downflix.win']
        self.base_link = 'https://en.downflix.win'
        self.search_link = '/%s-%s/'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + self.search_link % (title, year)
            return url
        except Exception:
            
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            holder = self.scraper.get(url, headers=headers).content
            Alternates = re.compile('<button class="text-capitalize dropdown-item" value="(.+?)"',
                                    re.DOTALL).findall(holder)
            for alt_link in Alternates:
                alt_url = alt_link.split("e=")[1]
                valid, host = source_utils.is_host_valid(alt_url, hostDict)
                sources.append({'source': host, 'quality': '1080p', 'language': 'en',
                                'url': alt_url, 'info': [], 'direct': False, 'debridonly': False})
            return sources
        except Exception:
            
            return

    def resolve(self, url):
        return directstream.googlepass(url)
