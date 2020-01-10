# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project
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

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import debrid
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rlsbb.ru','rlsbb.to','rlsbb.com','rlsbb.unblocked.cx']
        self.base_link = 'http://rlsbb.ru'
        self.search_base_link = 'http://search.rlsbb.ru'
        self.search_cookie = 'serach_mode=rlsbb'
        self.search_link = '/lib/search526049.php?phrase=%s&pindex=1&content=true'
        self.scraper = cfscrape.create_scraper()


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
            if url is None:
                return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            if debrid.status() is False:
                return sources

            hostDict = hostprDict + hostDict

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            premDate = ''

            query = '%s %s' % (title, hdlr)
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            query = query.replace("&", "and")
            query = query.replace("  ", " ")
            query = query.replace(" ", "-")

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            url = "http://rlsbb.ru/" + query
            # log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

            if 'tvshowtitle' not in data:
                url = url + "-1080p"

            r = self.scraper.get(url).content

            if r is None and 'tvshowtitle' in data:
                season = re.search('S(.*?)E', hdlr)
                season = season.group(1)
                query = title
                query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)
                query = query + "-S" + season
                query = query.replace("&", "and")
                query = query.replace("  ", " ")
                query = query.replace(" ", "-")
                url = "http://rlsbb.ru/" + query
                r = self.scraper.get(url).content

            # for loopCount in range(0,2):
                # if loopCount == 1 or (r is None and 'tvshowtitle' in data):

                    # premDate = re.sub('[ \.]','-',data['premiered'])
                    # query = re.sub('[\\\\:;*?"<>|/\-\']', '', data['tvshowtitle'])
                    # query = query.replace("&", " and ").replace("  ", " ").replace(" ", "-")
                    # query = query + "-" + premDate

                    # url = "http://rlsbb.ru/" + query
                    # url = url.replace('The-Late-Show-with-Stephen-Colbert', 'Stephen-Colbert')

                    # r = self.scraper.get(url).content

            posts = client.parseDOM(r, "div", attrs={"class": "content"})

            items = []
            for post in posts:
                try:
                    u = client.parseDOM(post, 'a', ret='href')

                    for i in u:
                        try:
                            name = str(i)
                            tit = name.rsplit('/', 1)[1]
                            t = tit.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
                            if cleantitle.get(t) != cleantitle.get(title):
                                continue

                            if hdlr in name.upper():
                                items.append(name)
                            # elif len(premDate) > 0 and premDate in name.replace(".","-"): items.append(name)

                        except:
                            source_utils.scraper_error('RLSBB')
                            pass

                except:
                    source_utils.scraper_error('RLSBB')
                    pass

                # if len(items) > 0:
                    # break

            seen_urls = set()
            for item in items:
                try:
                    info = []

                    url = str(item)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    if url in seen_urls:
                        continue

                    seen_urls.add(url)

                    host = url.replace("\\", "")
                    host2 = host.strip('"')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host2.strip().lower()).netloc)[0]

                    if not host in hostDict:
                        continue

                    if any(x in host2 for x in ['.rar', '.zip', '.iso']):
                        continue

                    quality, info = source_utils.get_release_quality(host2)

                    try:
                        size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', name)[0]
                        div = 1 if size.endswith('GB') else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass

                    info = ' | '.join(info)

                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': host2, 'info': info, 'direct': False, 'debridonly': True})

                except:
                    source_utils.scraper_error('RLSBB')
                    pass

            return sources
        except:
            source_utils.scraper_error('RLSBB')
            return sources


    def resolve(self, url):
        return url
