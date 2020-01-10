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

import re,urllib,urlparse
from liptonscrapers.modules import cache,cleantitle,client,control,debrid,source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pirateproxy.live', 'thepiratebay.org', 'thepiratebay.fun', 'thepiratebay.asia', 'tpb.party', 'thepiratebay3.org', 'thepiratebayz.org', 'thehiddenbay.com', 'piratebay.live', 'thepiratebay.zone']
        self._base_link = None 
        self.search_link = '/s/?q=%s&page=0&&video=on&orderby=99'
        self.min_seeders = int(control.setting('torrent.min.seeders'))


    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
        return self._base_link

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None:
                return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            if debrid.status() is False: raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            query = '%s S%02dE%02d' % (
                data['tvshowtitle'],
                int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'],
                data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|<|>|\|)', ' ', query)
            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)
            html = client.request(url)
            html = html.replace('&nbsp;', ' ')
            try:
                results = client.parseDOM(html, 'table', attrs={'id': 'searchResult'})[0]
            except Exception:
                return sources
            rows = re.findall('<tr(.+?)</tr>', results, re.DOTALL)
            if rows == None:
                return sources
            for entry in rows:
                try:
                    try:
                        name = re.findall('class="detLink" title=".+?">(.+?)</a>', entry, re.DOTALL)[0]
                        name = client.replaceHTMLCodes(name)

                        if not cleantitle.get(title) in cleantitle.get(name):
                            continue
                    except Exception:
                        continue
                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == hdlr:
                        continue
                    try:
                        seeders = int(re.findall('<td align="right">(.+?)</td>', entry, re.DOTALL)[0])
                    except Exception:
                        continue
                    if self.min_seeders > seeders:
                        continue
                    try:
                        link = 'magnet:%s' % (re.findall('a href="magnet:(.+?)"', entry, re.DOTALL)[0])
                        link = str(client.replaceHTMLCodes(link).split('&tr')[0])
                    except Exception:
                        continue
                    quality, info = source_utils.get_release_quality(name, name)
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', entry)[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except Exception:
                        pass
                    info = ' | '.join(info)
                    sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': True})
                except Exception:
                    continue
            check = [i for i in sources if not i['quality'] == 'CAM']
            if check:
                sources = check
            return sources
        except Exception:
            return sources

    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'https://%s' % domain
                    result = client.request(url, limit=1, timeout='10')
                    result = re.findall('<input type="submit" title="(.+?)"', result, re.DOTALL)[0]
                    if result and 'Pirate Search' in result:
                        return url
                except Exception:
                    pass
        except Exception:
            pass
        return fallback

    def resolve(self, url):
        return url
