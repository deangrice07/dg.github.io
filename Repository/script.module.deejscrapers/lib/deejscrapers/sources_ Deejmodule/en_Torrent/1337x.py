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
from liptonscrapers.modules import client
from liptonscrapers.modules import debrid,source_utils,control

class source:

    def __init__(self):
        self.priority = 1
        self.domains = ['1337x.to', '1337x.st', '1337x.is']
        self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru'] 
        self.base_link = 'https://1337x.to/'
        self.search_link = '/search/%s/1/'
        self.min_seeders = int(control.setting('torrent.min.seeders'))

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return sources
            if debrid.status() is False: raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s s%02de%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            try:
                posts = client.parseDOM(r, 'div', attrs={'class': 'box-info'})
                for post in posts:
                    data = client.parseDOM(post, 'a', ret='href')
                    u = [i for i in data if '/torrent/' in i]
                    for u in u:
                        match = '%s %s' % (title, hdlr)
                        match = match.replace('+', '-').replace(' ','-').replace(':-', '-').replace('---','-')
                        if not match in u: continue
                        u = self.base_link + u
                        r = client.request(u)
                        r = client.parseDOM(r, 'div', attrs={'class': 'torrent-category-detail clearfix'})
                        for t in r:
                            link = re.findall('href="magnet:(.+?)" onclick=".+?"', t)[0]
                            link = 'magnet:%s' % link
                            link = str(client.replaceHTMLCodes(link).split('&tr')[0])
                            seeds = int(re.compile('<span class="seeds">(.+?)</span>').findall(t)[0])
                            if self.min_seeders > seeds:
                                continue
                            quality, info = source_utils.get_release_quality(link, link)
                            try:
                                size = re.findall('<strong>Total size</strong> <span>(.+?)</span>', t)
                                for size in size:
                                    size = '%s' % size
                                    info.append(size)
                            except BaseException:
                                pass
                            info = ' | '.join(info)
                            sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': True})
            except:
                return
            return sources
        except :
            return sources

    def resolve(self, url):
        return url

