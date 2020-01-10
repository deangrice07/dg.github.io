# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re,requests
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['niter-movies.com']
        self.base_link = 'https://niter-movies.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0', 'Referer': self.base_link}
        self.session = requests.Session()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            mtitle = cleantitle.geturl(title)
            url = self.base_link + '/movie/%s-%s-streaming-online/' % (mtitle, year)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            hostDict = hostDict + hostprDict
            r = self.session.get(url, headers=self.headers).content
            pattern = "player\.src\(\'([0-9a-zA-Z-/._?=&:]+)\'"
            match = re.compile(pattern).findall(r)
            for url in match:
                valid, host = source_utils.is_host_valid(url, hostDict)
                quality, info = source_utils.get_release_quality(url, url)
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


