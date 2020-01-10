# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re,requests,urlparse
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hdmo.tv']
        self.base_link = 'https://hdmo.tv'
        self.search_link = '/?s=%s'
        self.ajax_link = '/wp-admin/admin-ajax.php'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0', 'Referer': self.base_link}
        self.session = requests.Session()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search = cleantitle.getsearch(title)
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % (search.replace(':', ' ').replace(' ', '+'))
            r = self.session.get(url, headers=self.headers).content
            movie_scrape = re.compile('<div class="title".+?href="(.+?)">(.+?)</a>.+?class="year">(.+?)</span>', re.DOTALL).findall(r)
            for movie_url, movie_title, movie_year in movie_scrape:
                if cleantitle.get(title) in cleantitle.get(movie_title):
                    if year in str(movie_year):
                        return movie_url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            search = cleantitle.getsearch(tvshowtitle)
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % (search.replace(':', ' ').replace(' ', '+'))
            r = self.session.get(url, headers=self.headers).content
            tv_scrape = re.compile('<div class="title".+?href="(.+?)">(.+?)</a>.+?class="year">(.+?)</span>', re.DOTALL).findall(r)
            for tv_url, tv_title, tv_year in tv_scrape:
                if cleantitle.get(tvshowtitle) in cleantitle.get(tv_title):
                    if year in str(tv_year):
                        return tv_url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            url = url[:-1]
            url = url.replace('/tvshows/', '/episodes/')
            url = url + '-%sx%s' % (season, episode)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None:
                return sources
            hostDict = hostprDict + hostDict
            r = self.session.get(url, headers=self.headers).content
            regex = re.compile("data-type='(.+?)' data-post='(.+?)' data-nume='(\d+)'>", re.DOTALL).findall(r)
            for data_type, post, nume in regex:
                customheaders = {
                    'Host': 'hdmo.tv',
                    'Accept': '*/*',
                    'Origin': 'https://hdmo.tv',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                    'Referer': url,
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                post_link = urlparse.urljoin(self.base_link, self.ajax_link)
                payload = {'action': 'doo_player_ajax', 'post': post, 'nume': nume, 'type': data_type}
                r = self.session.post(post_link, headers=customheaders, data=payload)
                i = r.content
                p = re.compile('<iframe.+?src="(.+?)"', re.DOTALL).findall(i)
                for url in p:
                    quality, info = source_utils.get_release_quality(url, url)
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


