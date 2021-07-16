# -*- coding: utf-8 -*-


import re
import traceback

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote
except ImportError: from urllib.parse import urlencode, quote

from revolutionscrapers.modules import cache, cleantitle, client, debrid, log_utils, source_utils, workers, utils
from revolutionscrapers.modules import dom_parser2 as dom
from revolutionscrapers.sources_revolutionscrapers import cfScraper

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['1337x.to', '1337x.st', '1337x.is', '1337x.unblocker.cc', '1337x.se', '1337x.eu', '1337x.ws']
        self._base_link = None

    def movie(self, imdb, title, localtitle, aliases, year):
        if debrid.status() is False:
            return

        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        if debrid.status() is False:
            return

        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if debrid.status() is False:
            return

        try:
            if url is None:
                return

            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []
            self.items = []
            if url is None:
                return self._sources

            if debrid.status() is False:
                raise Exception()

            if self._base_link is None:
                self.base_link = cache.get(self.__get_base_url, 240, 'https://%s' % self.domains[0])

            self.tvsearch = '%s/sort-category-search/%s/TV/seeders/desc/1/' % (self.base_link, '%s')
            self.moviesearch = '%s/sort-category-search/%s/Movies/size/desc/1/' % (self.base_link, '%s')

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])
                                        ) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'],
                int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'],
                data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            urls = []
            if 'tvshowtitle' in data:
                urls.append(self.tvsearch % (quote(query)))
                '''
                Why spam for multiple pages, since it gives plenty on each page?

                urls.append(self.tvsearch.format(quote(query), '2'))
                urls.append(self.tvsearch.format(quote(query), '3'))
                '''
            else:
                urls.append(self.moviesearch % (quote(query)))
                '''
                Why spam for multiple pages, since it gives plenty on each page?

                urls.append(self.moviesearch.format(quote(query), '2'))
                urls.append(self.moviesearch.format(quote(query), '3'))
                '''
            threads = []
            for url in urls:
                threads.append(workers.Thread(self._get_items, url))
            [i.start() for i in threads]
            [i.join() for i in threads]

            self.hostDict = hostDict + hostprDict
            threads2 = []
            for i in self.items:
                threads2.append(workers.Thread(self._get_sources, i))
            [i.start() for i in threads2]
            [i.join() for i in threads2]

            return self._sources
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            return self._sources

    def _get_items(self, url):
        try:
            r = cfScraper.get(url).content
            posts = client.parseDOM(r, 'tbody')[0]
            posts = client.parseDOM(posts, 'tr')
            for post in posts:
                data = dom.parse_dom(post, 'a', req='href')[1]
                link = urljoin(self.base_link, data.attrs['href'])
                name = data.content
                t = name.split(self.hdlr)[0]

                if not cleantitle.get(re.sub('(|)', '', t)) == cleantitle.get(self.title):
                    continue

                try:
                    y = re.findall('[\.|\(|\[|\s|\_|\-](S\d+E\d+|S\d+)[\.|\)|\]|\s|\_|\-]', name, re.I)[-1].upper()
                except BaseException:
                    y = re.findall('[\.|\(|\[|\s\_|\-](\d{4})[\.|\)|\]|\s\_|\-]', name, re.I)[-1].upper()
                if not y == self.hdlr:
                    continue

                try:
                    size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
                    dsize, isize = utils._size(size)
                except BaseException:
                    dsize, isize = 0, ''

                self.items.append((name, link, isize, dsize))
            return self.items
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            return self.items

    def _get_sources(self, item):
        try:
            name = item[0]
            quality, info = source_utils.get_release_quality(name, item[1])
            info.insert(0, item[2])
            data = cfScraper.get(item[1]).content
            data = client.parseDOM(data, 'a', ret='href')
            url = [i for i in data if 'magnet:' in i][0]
            url = url.split('&tr')[0]
            info = ' | '.join(info)

            self._sources.append(
                {'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False,
                 'debridonly': True, 'size': item[3]})
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('1337x - Exception: \n' + str(failure))
            pass

    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'https://%s' % domain
                    result = cfScraper.get(url).content
                    search_n = re.findall('<input type="search" placeholder="(.+?)"', result, re.DOTALL)[0]
                    if search_n and 'Search for torrents..' in search_n:
                        return url
                except Exception:
                    pass
        except Exception:
            pass

        return fallback

    def resolve(self, url):
        return url
