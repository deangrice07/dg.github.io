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
import urllib
import urlparse

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import dom_parser
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['cinenator.com']
        self.base_link = 'http://www.cinenator.com'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
                                                                    year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(
                [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)
            url = self.scraper.get(url).url

            if season == 1 and episode == 1:
                season = episode = ''

            r = self.scraper.get(url).content
            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'episodios'})
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*%s' % ('-%sx%s' % (season, episode)))})[
                0].attrs['href']

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            rel = dom_parser.parse_dom(r, 'div', attrs={'id': 'info'})
            rel = dom_parser.parse_dom(rel, 'div', attrs={'itemprop': 'description'})
            rel = dom_parser.parse_dom(rel, 'p')
            rel = [re.sub('<.+?>|</.+?>', '', i.content) for i in rel]
            rel = [re.findall('release:\s*(.*)', i, re.I) for i in rel]
            rel = [source_utils.get_release_quality(i[0]) for i in rel if i]
            quality, info = (rel[0]) if rel else ('SD', [])

            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'links'})
            r = dom_parser.parse_dom(r, 'table')
            r = dom_parser.parse_dom(r, 'tr', attrs={'id': re.compile('\d+')})
            r = [dom_parser.parse_dom(i, 'td') for i in r]
            r = [(i[0], re.sub('<.+?>|</.+?>', '', i[1].content).strip()) for i in r if len(r) >= 1]
            r = [(dom_parser.parse_dom(i[0], 'a', req='href'), i[1]) for i in r]
            r = [(i[0][0].attrs['href'], i[1]) for i in r if i[0]]

            info = ' | '.join(info)

            for link, hoster in r:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                sources.append(
                    {'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'info': info, 'direct': False,
                     'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if self.base_link in url:
                r = self.scraper.get(url).content
                r = dom_parser.parse_dom(r, 'div', attrs={'class': 'cupe'})
                r = dom_parser.parse_dom(r, 'div', attrs={'class': 'reloading'})
                url = dom_parser.parse_dom(r, 'a', req='href')[0].attrs['href']

            return url
        except:
            return

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = self.scraper.get(query).content

            r = dom_parser.parse_dom(r, 'article')
            r = [(dom_parser.parse_dom(i, 'div', attrs={'class': 'title'}),
                  dom_parser.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]
            r = [(dom_parser.parse_dom(i[0][0], 'a', req='href'), i[1][0].content) for i in r if i[0] and i[1]]
            r = [(i[0][0].attrs['href'], i[0][0].content, i[1]) for i in r if i[0]]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return
