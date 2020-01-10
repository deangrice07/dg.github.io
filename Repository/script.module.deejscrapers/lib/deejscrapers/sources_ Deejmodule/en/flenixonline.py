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
# Testing @Cy4Root 01-10-2019 movie: Anna (2019)

import re
from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['new123movies.co', 'flenix.online', 'flenix-hd.online']
        self.base_link = 'http://new123movies.co'
        self.search_link = '/?s=%s+%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('-', '+')
            url = self.base_link + self.search_link % (title, year)
            searchPage = self.scraper.get(url).content
            results = re.compile('<a href="(.+?)" title="(.+?)">').findall(searchPage)
            for url, checkit in results:
                zcheck = '%s (%s)' % (title, year)
                zcheck2 = '%s %s' % (title, year)
                if zcheck.lower() in checkit.lower():
                    return url
                elif zcheck2.lower() in checkit.lower():
                    return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            hostDict = hostDict + hostprDict
            sourcesPage = self.scraper.get(url).content
            results = re.compile('<iframe.+?src="(.+?)"').findall(sourcesPage)
            for url in results:
                valid, host = source_utils.is_host_valid(url, hostDict)
                if valid:
                    quality, info = source_utils.get_release_quality(url, url)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


