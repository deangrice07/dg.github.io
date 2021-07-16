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

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from six import ensure_text
from six.moves import zip

from revolutionscrapers.modules import cleantitle, client, source_utils, log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['myvideolinks.net', 'iwantmyshow.tk', 'new.myvideolinks.net']
        self.base_link = 'https://new.myvideolinks.net'
        #self.base_link = 'http://kita.myvideolinks.net'
        self.search_link = '/?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
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
        except Exception:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'],
                int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'],
                data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            r = client.request(self.base_link)
            search_base = client.parseDOM(r, 'form', ret='action')[0]
            #log_utils.log(search_base)
            url = urljoin(search_base, self.search_link)
            #url = urljoin(self.base_link, self.search_link)
            url = url % quote_plus(query)

            r = client.request(url)

            r = client.parseDOM(r, 'h2')

            z = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a'))

            if 'tvshowtitle' in data:
                posts = [(i[1], i[0]) for i in z]
            else:
                posts = [(i[1], i[0]) for i in z]

            hostDict = hostprDict + hostDict

            items = []

            for post in posts:
                try:
                    try:
                        t = ensure_text(post[0])
                    except:
                        t = post[0]

                    u = client.request(post[1])

                    u = re.findall('\'(http.+?)\'', u) + re.findall('\"(http.+?)\"', u)
                    u = [i for i in u if '/embed/' not in i]
                    u = [i for i in u if 'youtube' not in i]

                    try:
                        s = re.search('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', post)
                        s = s.groups()[0] if s else '0'
                    except:
                        s = '0'
                        pass

                    items += [(t, i, s) for i in u]

                except:
                    pass

            for item in items:
                try:
                    url = item[1]

                    url = client.replaceHTMLCodes(url)
                    url = ensure_text(url)

                    void = ('.rar', '.zip', '.iso', '.part', '.png', '.jpg', '.bmp', '.gif')
                    if url.endswith(void):
                        raise Exception()

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid:
                        raise Exception()

                    host = client.replaceHTMLCodes(host)
                    host = ensure_text(host)

                    name = item[0]
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name, flags=re.I)
                    if not cleantitle.get(t) == cleantitle.get(title):
                        raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == hdlr:
                        raise Exception()

                    quality, info = source_utils.get_release_quality(name, url)

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', item[2])[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '[B]%.2f GB[/B]' % size
                        info.append(size)
                    except:
                        pass

                    info = ' | '.join(info)

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                                'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            import traceback
            fail = traceback.format_exc()
            log_utils.log('MYVIDEOLINK ERROR: ' + str(fail))
            return sources


    def resolve(self, url):
        return url
