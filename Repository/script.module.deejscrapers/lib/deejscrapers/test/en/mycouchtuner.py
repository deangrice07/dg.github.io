# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mycouchtuner.li', 'ecouchtuner.eu']
        self.base_link = 'https://2mycouchtuner.one'
        self.search_link = '/watch-%s-online/'
        self.scraper = cfscrape.create_scraper()

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            tvshowtitle = cleantitle.geturl(tvshowtitle)
            url = self.base_link + self.search_link % tvshowtitle
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            r = client.request(url)
            match = re.compile('2mycouchtuner\..+?/(.+?)/\' title=\'.+? Season ' + season + ' Episode ' + episode + '\:').findall(r)
            for url in match:
                url = 'https://mycouchtuner.li/' + url
                return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            headers = {'Referer': url, 'User-Agent': 'Mozilla/5.0'}
            r = self.scraper.get(url, headers=headers).content
            match = re.compile('<iframe class=\'lazyload\' data-src=\'//(.+?)/(.+?)\'').findall(r)
            print match
            for host, ext in match:
                url = 'https://%s/%s' % (host, ext)
                sources.append({
                    'source': host,
                    'quality': 'SD',
                    'language': 'en',
                    'url': url,
                    'direct': False,
                    'debridonly': False
                })
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
