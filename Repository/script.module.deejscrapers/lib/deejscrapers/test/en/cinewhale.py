# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
from liptonscrapers.modules import client,cleantitle,source_utils,cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cinewhale.com']
        self.base_link = 'https://cinewhale.com'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + '/movies/%s-%s/' % (title,year)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                qual = re.compile('class="quality">(.+?)<').findall(r)
                for i in qual:
                    if 'HD' in i:
                        quality = 'HD'
                    else:
                        quality = 'SD'
                match = re.compile('<a href="(.+?)" target="_blank" class').findall(r)
                for url in match:
                    r = self.scraper.get(url).content
                    match = re.compile('iframe src=&quot;(.+?)/&quot;').findall(r)
                    for url in match:
                        info = i
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False}) 
            except:
                return
        except Exception:
            return
        return sources


    def resolve(self, url):
        return url
