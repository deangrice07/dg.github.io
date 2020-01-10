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
# Testing @Cy4Root 11-11-2019 movie: Anna 2019
import re
from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import client
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import more_sources
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ganool.fun', 'ganool.rip']
        self.base_link = 'https://ganool.fun'
        self.search_link = '/?s=%s+%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('-', '+')
            url = self.base_link + self.search_link % (title, year)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            hostDict = hostDict + hostprDict
            sources = []
            r = self.scraper.get(url).content
            u = client.parseDOM(r, "div", attrs={"class": "ml-item"})
            for i in u:
                t = re.compile('<a href="(.+?)"').findall(i)
                for r in t:
                    t = self.scraper.get(r).content
                    results1 = re.compile('<a href="(.+?)" class="lnk').findall(t)
                    for url in results1:
                        if self.base_link in url:
                            continue
                        quality, info = source_utils.get_release_quality(url, url)
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                    results2 = re.compile('<iframe src="(.+?)"').findall(t)
                    for link in results2:
                        if "gomostream.com" in link:
                            for source in more_sources.more_gomo(link, hostDict):
                                sources.append(source)
                        else:
                            if "//ouo.io/" in link:
                                continue
                            quality, info = source_utils.get_release_quality(link, link)
                            valid, host = source_utils.is_host_valid(link, hostDict)
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


