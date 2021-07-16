# -*- coding: utf-8 -*-
# -Cleaned and Checked on 03-04-2019 by JewBMX in Scrubs.

import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote
except ImportError: from urllib.parse import urlencode, quote

from revolutionscrapers.modules import cache
from revolutionscrapers.modules import client
from revolutionscrapers.modules import dom_parser2 as dom
from revolutionscrapers.modules import cleantitle
from revolutionscrapers.modules import debrid
from revolutionscrapers.modules import source_utils
from revolutionscrapers.modules import workers
from revolutionscrapers.modules import utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['limetorrents.info', 'limetorrents.co', 'limetor.com']
        self._base_link = None
        self.tvsearch = '/search/tv/{0}/'
        self.moviesearch = '/search/movies/{0}/'


    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
        return self._base_link


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except BaseException:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []
            self.items = []
            if url is None:
                return self._sources
            if debrid.status() is False: return
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            query = '%s S%02dE%02d' % (
            data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
            data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            if 'tvshowtitle' in data:
                url = self.tvsearch.format(quote(query))
                url = urljoin(self.base_link, url)
            else:
                url = self.moviesearch.format(quote(query))
                url = urljoin(self.base_link, url)
            self._get_items(url)
            self.hostDict = hostDict + hostprDict
            threads = []
            for i in self.items:
                threads.append(workers.Thread(self._get_sources, i))
            [i.start() for i in threads]
            [i.join() for i in threads]
            return self._sources
        except BaseException:
            return self._sources

    def _get_items(self, url):
        try:
            headers = {'User-Agent': client.agent()}
            r = client.request(url, headers=headers)
            posts = client.parseDOM(r, 'table', attrs={'class': 'table2'})[0]
            posts = client.parseDOM(posts, 'tr')
            for post in posts:
                data = dom.parse_dom(post, 'a', req='href')[1]
                link = urljoin(self.base_link, data.attrs['href'])
                name = data.content
                t = name.split(self.hdlr)[0]
                if not cleantitle.get(re.sub('(|)', '', t)) == cleantitle.get(self.title): continue
                try:
                    y = re.findall('[\.|\(|\[|\s|\_|\-](S\d+E\d+|S\d+)[\.|\)|\]|\s|\_|\-]', name, re.I)[-1].upper()
                except BaseException:
                    y = re.findall('[\.|\(|\[|\s\_|\-](\d{4})[\.|\)|\]|\s\_|\-]', name, re.I)[-1].upper()
                if not y == self.hdlr: continue
                try:
                    size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
                    dsize, isize = utils._size(size)
                except BaseException:
                    dsize, isize = 0, ''
                self.items.append((name, link, isize, dsize))
            return self.items
        except BaseException:
            return self.items


    def _get_sources(self, item):
        try:
            name = item[0]
            data = client.request(item[1])
            url = re.search('''href=["'](magnet:\?[^"']+)''', data).groups()[0]
            url = url.split('&tr')[0]
            quality, info = source_utils.get_release_quality(name, url)
            info.insert(0, item[2])
            info = ' | '.join(info)
            self._sources.append(
                {'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False,
                 'debridonly': True, 'size': item[3]})
        except BaseException:
            pass


    def resolve(self, url):
        return url


    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'https://%s' % domain
                    result = client.request(url, limit=1, timeout='5')
                    result = re.findall('<title>(.+?)</title>', result, re.DOTALL)[0]
                    if result and 'LimeTorrents' in result:
                        return url
                except Exception:
                    pass
        except Exception:
            pass
        return fallback