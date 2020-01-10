# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cmovieshd.net']
        self.base_link = 'https://cmovieshd.net'
        self.search_link = '/search/?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('-', '+')
            u = self.base_link + self.search_link % title
            u = client.request(u)
            i = client.parseDOM(u, "div", attrs={"class": "movies-list"})
            for r in i:
                r = re.compile('<a href="(.+?)"').findall(r)
                for url in r:
                    title = cleantitle.geturl(title).replace("+", "-")
                    if not title in url:
                        continue
                    return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            url = url + 'watch/'
            r = client.request(url)
            qual = re.compile('class="quality">(.+?)<').findall(r)
            for i in qual:
                if 'HD' in i:
                    quality = '720p'
                else:
                    quality = 'SD'
            r = client.parseDOM(r, "div", attrs={"id": "list-eps"})
            for i in r:
                t = re.compile('<a href="(.+?)"').findall(i)
                for url in t:
                    t = client.request(url)
                    t = client.parseDOM(t, "div", attrs={"id": "content-embed"})
                    for u in t:
                        i = re.findall('src="(.+?)"', u)[0].replace('load_player.html?e=', 'episode/embed/')
                        i = client.request(i).replace("\\", "")
                        u = re.findall('"(https.+?)"', i)
                        for url in u:
                            sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})

                return sources
        except Exception:
            return

    def resolve(self, url):
        return url
