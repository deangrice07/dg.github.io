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
# Testing @Cy4Root 17-10-2019 movie: Anna (2019)

import re
import urllib
import urlparse

from liptonscrapers.modules import cfscrape, cleantitle, client, debrid, source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['yts.am']
        self.base_link = 'https://yts.lt/'
        self.search_link = '/browse-movies/%s/all/all/0/latest'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        if debrid.status() is False:
            return

        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources
            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            query = '%s %s' % (data['title'], data['year'])

            url = self.search_link % urllib.quote(query)
            url = urlparse.urljoin(self.base_link, url)
            html = self.scraper.get(url).content
            try:
                results = client.parseDOM(html, 'div', attrs={'class': 'row'})[2]
            except Exception:
                return sources

            items = re.findall('class="browse-movie-bottom">(.+?)</div>\s</div>', results, re.DOTALL)
            if items is None:
                return sources

            for entry in items:
                try:
                    try:
                        link, name = re.findall('<a href="(.+?)" class="browse-movie-title">(.+?)</a>', entry, re.DOTALL)[0]
                        name = client.replaceHTMLCodes(name)
                        if not cleantitle.get(data['title']) in cleantitle.get(name):
                            continue
                    except Exception:
                        continue
                    y = entry[-4:]
                    if not y == data['year']:
                        continue

                    response = self.scraper.get(link).content
                    try:
                        entries = client.parseDOM(response, 'div', attrs={'class': 'modal-torrent'})
                        for torrent in entries:
                            link, name = re.findall('href="magnet:(.+?)" class="magnet-download download-torrent magnet" title="(.+?)"', torrent, re.DOTALL)[0]
                            link = 'magnet:%s' % link
                            link = str(client.replaceHTMLCodes(link).split('&tr')[0])
                            quality, info = source_utils.get_release_quality(name, name)
                            try:
                                size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', torrent)[-1]
                                div = 1 if size.endswith(('GB', 'GiB')) else 1024
                                size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                                size = '[B]%.2f GB[/B]' % size
                                info.append(size)
                            except Exception:
                                pass

                            info = ' | '.join(info)

                            sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en',
                                            'url': link, 'info': info, 'direct': False, 'debridonly': True})
                    except Exception:
                        continue
                except Exception:
                    continue

            return sources
        except Exception:
            return sources

    def resolve(self, url):
        return url
