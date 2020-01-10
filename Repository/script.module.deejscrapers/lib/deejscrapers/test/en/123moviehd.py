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
        self.domains = ['123moviehd.cc']
        self.base_link = 'https://123moviehd.cc'
        self.search_link = '/%s-%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + self.search_link % (title, year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            r = requests.get(url).content
            try:
                qual = re.compile('class="quality">(.+?)<').findall(r)
                for i in qual:
                    if 'HD' in i:
                        quality = '1080p'
                    else:
                        quality = 'SD'
                match = re.compile('<iframe.+?src="(.+?)"').findall(r)
                for url in match:
                    if 'youtube' in url:
                        continue
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid:
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
