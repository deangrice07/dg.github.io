# -*- coding: utf-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# @shellc0de wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################

import re
import requests
import traceback

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode

from revolutionscrapers.modules import cleantitle, log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['iwaatch.com']
        self.base_link = 'https://iwaatch.com'
        self.search_link = '/?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('iWAATCH - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            year = data['year']

            search_id = cleantitle.getsearch(title.lower())
            url = urljoin(self.base_link, self.search_link % (search_id.replace(' ', '+')))
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'DNT': '1'
            }

            response = requests.Session()
            r = response.get(url, headers=headers).text
            movie_scrape = re.compile('<h2 class="h2 p-title.+?a href="(.+?)".+?div class="post-title">(.+?)<', re.DOTALL).findall(r)

            for movie_url, movie_title in movie_scrape:
                if cleantitle.getsearch(title).lower() == cleantitle.getsearch(movie_title).lower():
                    r = response.get(movie_url, headers=headers).text
                    year_data = re.findall('<h2 style="margin-bottom: 0">(.+?)</h2>', r, re.IGNORECASE)[0]
                    if year == year_data:
                        links = re.findall(r"<a href='(.+?)'>(\d+)p<\/a>", r)

                        for link, quality in links:

                            if '1080' in quality:
                                quality = '1080p'
                            elif '720' in quality:
                                quality = '720p'
                            elif '480' in quality:
                                quality = 'SD'
                            else:
                                quality = 'SD'

                            sources.append({'source': 'Direct', 'quality': quality, 'language': 'en', 'url': link+'|Referer=https://iwaatch.com/movie/' + title, 'direct': True, 'debridonly': False})
            return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('iWAATCH - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
