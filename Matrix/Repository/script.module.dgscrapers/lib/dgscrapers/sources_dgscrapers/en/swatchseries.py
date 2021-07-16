# -*- coding: utf-8 -*-
# -Cleaned and Checked on 04-30-2020 by Tempest.

import re
import traceback

try: from urlparse import parse_qs, urlparse
except ImportError: from urllib.parse import parse_qs, urlparse
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode

from six import ensure_str

from revolutionscrapers.modules import cleantitle
from revolutionscrapers.modules import client
from revolutionscrapers.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['dwatchseries.to', 'swatchseries.to']
        self.base_link = 'https://www1.swatchseries.to'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('SwatchSeries - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            tit = cleantitle.get_query_(url['tvshowtitle'])
            tit = re.sub('[^A-Za-z0-9]+', '_', tit)
            url = '%s/episode/%s_s%s_e%s.html' % (self.base_link, tit, season, episode)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('SwatchSeries - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources
            hostDict = hostprDict + hostDict
            r = client.request(url)
            links = re.compile(r'''onclick="if \(confirm\('Delete link (.+?)'\)\)''', re.DOTALL).findall(r)
            links = [x for y, x in enumerate(links) if x not in links[:y]]
            for i in links:
                try:
                    url = i
                    url = client.replaceHTMLCodes(url)
                    url = ensure_str(url)
                    host = re.findall('([\w]+[.][\w]+)$', urlparse(url.strip().lower()).netloc)[0]
                    if host not in hostDict:
                        raise Exception()
                    host = ensure_str(host)
                    if 'vev' not in url:
                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except Exception:
                    pass

            return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('SwatchSeries - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
