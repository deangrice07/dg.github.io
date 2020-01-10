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
import urlparse

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import dom_parser
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.genre_filter = ['horror']
        self.domains = ['horrorkino.do.am']
        self.base_link = 'http://horrorkino.do.am/'
        self.search_link = 'video/shv'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
                                                                    year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = self.scraper.get(urlparse.urljoin(self.base_link, url)).content
            r = re.findall('''vicode\s*=\s*["'](.*?)["'];''', r)[0].decode('string_escape')
            r = dom_parser.parse_dom(r, 'iframe', req='src')
            r = [i.attrs['src'] for i in r]

            for i in r:
                valid, host = source_utils.is_host_valid(i, hostDict)
                if not valid: continue

                sources.append(
                    {'source': host, 'quality': 'SD', 'language': 'de', 'url': i, 'direct': False, 'debridonly': False,
                     'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = self.scraper.post(urlparse.urljoin(self.base_link, self.search_link),
                                  data={'query': cleantitle.query(titles[0])})

            r = dom_parser.parse_dom(r, 'li', attrs={'class': 'entTd'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 've-screen'}, req='title')
            r = [(dom_parser.parse_dom(i, 'a', req='href'), i.attrs['title'].split(' - ')[0]) for i in r]
            r = [(i[0][0].attrs['href'], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return
