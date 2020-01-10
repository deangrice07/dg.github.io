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

import re, requests

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['s1.dlserver.info']
        self.base_link_movie = 'http://s1.dlserver.info/Movie/'
        self.base_link_tv = 'http://s1.dlserver.info/serial/%s/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.get_query(title)
            self.title = '%s.%s/' % (title, year)
            url = self.base_link_movie + self.title
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            title = cleantitle.get_query(tvshowtitle)
            url = self.base_link_tv % title
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            self.se = 'S%02dE%02d' % (int(season), int(episode))
            self.season = '%02d-' % int(season)
            if not url: return
            url = url
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            result = url
            if 'serial' in result:
                try:
                    r = requests.get(result, timeout=10).content
                    results = re.findall('a href="(' + self.season + '.+?)"', r)
                    for results in results:
                        if 'Dubbed' in results: continue
                        result2 = result + results
                        r = requests.get(result2, timeout=10).content
                        r = re.findall('a href="(.+?)"',r)
                        for url in r:
                            if self.se not in url: continue
                            url = result2 + url
                            quality = source_utils.check_direct_url(url)
                            sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                except:
                    return
            else:
                try:
                    r = requests.get(result).content
                    r = re.compile('a href="(.+?)"').findall(r)
                    for url in r:
                        if any(x in url for x in ['Trailer', 'AUDIO']): continue
                        url = result + url
                        quality = source_utils.check_url(url)
                        sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                except:
                    return
            return sources
        except:
            return

    def resolve(self, url):
        return url
