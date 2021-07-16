# -*- coding: UTF-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# @tantrumdev wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################


import re
import traceback

try: from urlparse import parse_qs, urljoin, urlparse
except ImportError: from urllib.parse import parse_qs, urljoin, urlparse
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from six import ensure_text

from revolutionscrapers.modules import client, debrid, log_utils, source_utils
from revolutionscrapers.sources_revolutionscrapers import cfScraper


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rlsbb.com', 'rlsbb.ru', 'rlsbb.to']
        self.base_link = 'http://rlsbb.ru/'
        self.search_base_link = 'http://search.rlsbb.ru/'
        self.search_cookie = 'serach_mode=rlsbb'
        self.search_link = '/lib/search526049.php?phrase=%s&pindex=1&content=true'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
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
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            if debrid.status() is False:
                return sources

            hostDict = hostprDict + hostDict

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            premDate = ''

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'],
                int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'],
                data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            query = query.replace("&", "and")
            query = query.replace("  ", " ")
            query = query.replace(" ", "-")

            url = self.search_link % quote_plus(query)
            url = urljoin(self.base_link, url)

            url = "http://rlsbb.ru/" + query

            r = cfScraper.get(url).content

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
                r = cfScraper.get(url).content

            for loopCount in list(range(0, 2)):
                if loopCount == 1 or(r is None and 'tvshowtitle' in data):

                    #premDate = re.sub('[ \.]', '-', data['premiered'])
                    query = re.sub(r'[\\\\:;*?"<>|/\-\']', '', data['tvshowtitle'])
                    query = query.replace(
                        "&", " and ").replace(
                        "  ", " ").replace(
                        " ", "-")  # throw in extra spaces around & just in case
                    #query = query + "-" + premDate

                    url = "http://rlsbb.ru/" + query
                    url = url.replace('The-Late-Show-with-Stephen-Colbert', 'Stephen-Colbert')

                    r = cfScraper.get(url).content

                posts = client.parseDOM(r, "div", attrs={"class": "content"})
                #hostDict = hostprDict + hostDict
                items = []
                for post in posts:
                    try:
                        u = client.parseDOM(post, 'a', ret='href')
                        for i in u:
                            try:
                                name = str(i)
                                if hdlr in name.upper():
                                    items.append(name)
                                #elif len(premDate) > 0 and premDate in name.replace(".", "-"):
                                    #items.append(name)
                            except Exception:
                                failure = traceback.format_exc()
                                log_utils.log('RLSBB - Exception: \n' + str(failure))
                                pass
                    except Exception:
                        failure = traceback.format_exc()
                        log_utils.log('RLSBB - Exception: \n' + str(failure))
                        pass

                if len(items) > 0:
                    break

            seen_urls = set()

            for item in items:
                try:
                    info = []

                    url = str(item)
                    url = client.replaceHTMLCodes(url)
                    url = ensure_text(url)

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    host = url.replace("\\", "")
                    host2 = host.strip('"')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse(host2.strip().lower()).netloc)[0]

                    if host not in hostDict:
                        continue
                    if any(x in host2 for x in ['.rar', '.zip', '.iso', '.part']):
                        continue

                    quality, info = source_utils.get_release_quality(host2)

                    #try:
                    #    size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
                    #    div = 1 if size.endswith(('GB', 'GiB')) else 1024
                    #    size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
                    #    size = '%.2f GB' % size
                    #    info.append(size)
                    #except:
                    #    pass

                    info = ' | '.join(info)

                    host = client.replaceHTMLCodes(host)
                    host = ensure_text(host)
                    sources.append({'source': host, 'quality': quality, 'language': 'en',
                                    'url': host2, 'info': info, 'direct': False, 'debridonly': True})
                except Exception:
                    failure = traceback.format_exc()
                    log_utils.log('RLSBB - Exception: \n' + str(failure))
                    pass
            check = [i for i in sources if not i['quality'] == 'CAM']
            if check:
                sources = check
            return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
