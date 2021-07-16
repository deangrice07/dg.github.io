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

import re, traceback

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, unquote_plus
except ImportError: from urllib.parse import urlencode, unquote_plus

from revolutionscrapers.modules import debrid
from revolutionscrapers.modules import cleantitle
from revolutionscrapers.modules import client
from revolutionscrapers.modules import source_utils
from revolutionscrapers.modules import utils, log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['torrentquest.com']
        self.base_link = 'https://www.magnetdl.com/'
        self.search_link = '/{0}/{1}'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('Magnetdl - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('Magnetdl - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('Magnetdl - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if debrid.status() is False:
                raise Exception()

            if url is None:
                return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s s%02de%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))\
                if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub(u'(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = urljoin(self.base_link, self.search_link.format(query[0].lower(), cleantitle.geturl(query)))

            r = client.request(url)
            r = client.parseDOM(r, 'tbody')[0]
            posts = client.parseDOM(r, 'tr')
            posts = [i for i in posts if 'magnet:' in i]
            for post in posts:
                post = post.replace('&nbsp;', ' ')
                name = client.parseDOM(post, 'a', ret='title')[1]

                t = name.split(hdlr)[0]
                if not cleantitle.get(re.sub(r'(|)', '', t)) == cleantitle.get(title): continue

                try:
                    y = re.findall(u'[\.|\(|\[|\s|\_|\-](S\d+E\d+|S\d+)[\.|\)|\]|\s|\_|\-]', name, re.I)[-1].upper()
                except BaseException:
                    y = re.findall(u'[\.|\(|\[|\s\_|\-](\d{4})[\.|\)|\]|\s\_|\-]', name, re.I)[-1].upper()
                if not y == hdlr: continue

                links = client.parseDOM(post, 'a', ret='href')
                magnet = [i.replace('&amp;', '&') for i in links if 'magnet:' in i][0]
                url = magnet.split('&tr')[0]

                quality, info = source_utils.get_release_quality(name, url)
                try:
                    size = re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
                    dsize, isize = utils._size(size)
                except:
                    dsize, isize = 0, ''

                info.insert(0, isize)

                #try:
                    #info.append(name)
                #except Exception:
                    #pass

                info = ' | '.join(info)

                sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                'direct': False, 'debridonly': True, 'size': dsize})

            return sources
        except BaseException:
            failure = traceback.format_exc()
            log_utils.log('Magnetdl - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
