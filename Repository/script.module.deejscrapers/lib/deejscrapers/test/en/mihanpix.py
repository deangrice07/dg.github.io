# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re, urlparse, requests

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mihanpix.com']
        self.base_link = 'https://mihanpix.com'
        self.search_link = '/?s=%s+%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            title = cleantitle.geturl(url['title']).replace('-', '+')
            url = urlparse.urljoin(self.base_link, self.search_link % (title, url['year']))
            r = requests.get(url, timeout=10).content
            r = client.parseDOM(r, "h2", attrs={"class": "entry-title"})
            for u in r:
                u = re.compile('a href="(.+?)" rel=".+?">.+?<').findall(u)
                for r in u:
                    r = requests.get(r, timeout=10).content
                    r = client.parseDOM(r, "div", attrs={"id": "content"})
                    for t in r:
                        t = re.compile('a class="buttn .+?" href="(.+?)" target=".+?">').findall(t)
                        for url in t:
                            if 'mihanpix.com' in url: continue
                            if any(x in url for x in ['Trailer', 'Dubbed']): continue
                            quality = source_utils.check_url(url)
                            sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

