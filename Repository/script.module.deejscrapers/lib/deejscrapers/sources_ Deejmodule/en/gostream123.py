# -*- coding: utf-8 -*-
############################################################################################################################################################################                                                                                                                                       #                                                                                                                                                                          #
#                                                                                                                                                                          #
#    ##     .   **       #########.  ########   #########   ##     ##    #########   #########   #########   #########   #########   ########   #########   ##########     #
#    ##         ##       ##     ##     ###      ##     ##   ###    ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ##     ##     ###      ##     ##   ## #   ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ########      ###      ##     ##   ##  #  ##    #########   ##          ########    #########   ## ######   ########   ########    ##########     #
#    ##         ##       ##            ###      ##     ##   ##   # ##           ##   ##          ##    ##    ##     ##   ##          ##         ##    ##            ##     #
#    ##         ##       ##            ###      ##     ##   ##    ###           ##   ##          ##     ##   ##     ##   ##          ##         ##     ##           ##     #
#    #######    ##       ##     .      ###      #########   ##     ##    #########   ##########  ##      #   ##     ##   ##          ########   ##      #   ##########     #
############################################################################################################################################################################
# Testing @Cy4Root 07-11-2019 movie: Joker 2019

import re
from liptonscrapers.modules import client,cleantitle,source_utils,cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['gostream-123.com', 'gomovies123.today', 'movie-32.com']
        self.base_link = 'http://movie-32.com'
        self.search_link = '/?s=%s+%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            mvtitle = cleantitle.geturl(title)
            searchtit = mvtitle.replace('-', '+').replace('++', '+')
            url = self.base_link + self.search_link % (searchtit, year)
            r = self.scraper.get(url).content
            match = re.compile('<a href="(.+?)" title="(.+?)">').findall(r)
            for url, check in match:
                tity = '%s (%s)' % (title, year)
                if not cleantitle.get(tity) in cleantitle.get(check):
                    continue
                return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            r = self.scraper.get(url).content
            try:
                match = re.compile('<iframe .+? src="(.+?)"').findall(r)
                for url in match:
                    quality = source_utils.check_url(url)
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


