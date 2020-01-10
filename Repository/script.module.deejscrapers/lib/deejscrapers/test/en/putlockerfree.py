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
import re
from liptonscrapers.modules import client
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlockersfree.sc', 'putlockerfree.sc']
        self.base_link = 'https://putlockersfree.sc'
        self.search_link = '/search-query/%s+%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            mtitle = cleantitle.geturl(title)
            url = self.base_link + '/films/%s-%s/' % (mtitle, year)
            url = client.request(url, timeout='10', output='geturl')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            url = url + "watching.html/"
            r = client.request(url)
            t = re.compile('data-.+?="(.+?)".+?href="javascript:void').findall(r)
            for url in t:
                valid, host = source_utils.is_host_valid(url, hostDict)
                if valid:
                    quality, info = source_utils.get_release_quality(url, url)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


