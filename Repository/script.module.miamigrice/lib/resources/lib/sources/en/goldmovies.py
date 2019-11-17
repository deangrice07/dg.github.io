# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib
import urlparse

from resources.lib.modules import cleantitle, client, source_utils, log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['goldmovies.xyz']
        self.base_link = 'http://goldmovies.xyz'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
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

            if url is None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            query = '%s Season %d Episode %d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))if 'tvshowtitle' in data else '%s' % (data['title'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            year = data['year']
            search = cleantitle.getsearch(query.lower())
            url = urlparse.urljoin(self.base_link, self.search_link % (search.replace(' ', '+')))

            headers = {'Referer': self.base_link, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}
            r = client.request(url, headers=headers)

            scrape = re.compile('<div data-movie-id=.+?class="ml-item">\s+<a href="(.+?)" data-url="" class="ml-mask jt".+?oldtitle="(.+?)"').findall(r)

            for url, title_data in scrape:
                if cleantitle.getsearch(query).lower() == cleantitle.getsearch(title_data).lower():
                    r = client.request(url, headers=headers)
                    year_data = re.compile('<strong>Release:\s+</strong>\s+<a href=.+?rel="tag">(.+?)</a>').findall(r)
                    if year in year_data:
                        if 'tvshowtitle' in data:
                            year is None

                    parse_a_bitch = client.parseDOM(r, 'div', attrs={'id': 'lnk list-downloads'})
                    for url in parse_a_bitch:
                        gold_links = client.parseDOM(url, 'a', ret='href')

                    for url in gold_links:
                        quality = source_utils.check_sd_url(url)
                        url = url.split('php?')[1]
                        sources.append({'source': 'Direct', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

                return sources
        except Exception:
            return sources

    def resolve(self, url):
        return url