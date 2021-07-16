# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 02-24-2019 by JewBMX in Scrubs.

import re,urllib,urlparse
from revolutionscrapers.modules import cleantitle, source_utils
from revolutionscrapers.sources_revolutionscrapers import cfScraper


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['project-free-tv.ag','my-project-free.tv']
        self.base_link = 'http://www1.projectfreetv.ag'
        self.search_link = '/episode/%s-season-%s-episode-%s'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            url = clean_title
            return url
        except:
            return
 
 
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            tvshowtitle = url
            url = self.base_link + self.search_link % (tvshowtitle, int(season), int(episode))
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = cfScraper.get(url).content
            try:
                data = re.compile("callvalue\('.+?','.+?','(.+?)://(.+?)/(.+?)'\)").findall(r)
                for http,host,url in data:
                    url = '%s://%s/%s' % (http,host,url)
                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if valid:
                        sources.append({ 'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False })
            except:
                pass
            return sources
        except Exception:
            return


    def resolve(self, url):
        return url

