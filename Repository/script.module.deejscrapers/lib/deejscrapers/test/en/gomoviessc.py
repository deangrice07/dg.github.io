# -*- coding: UTF-8 -*-

################################
# https://cy4root.github.io    #
################################
import re
from liptonscrapers.modules import client,cleantitle,source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['gomovies.sc']
        self.base_link = 'https://gomovies.sc'
        self.search_movie = '/browsing-for/%s+%s/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('-', '+')
            i = self.base_link + self.search_movie % (title, year)
            i = client.request(i)
            i = client.parseDOM(i, "div", attrs={"class": "movies-list movies-list-full"})
            for r in i:
                r = re.compile('<a href="(https://gomovies.sc/movie/.+?)" .+? title=".+?"').findall(r)
                for url in r:
                    url = url + 'watching/'
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            r = client.request(url)
            u = client.parseDOM(r, "div", attrs={"id": "list-eps"})
            for i in u:
                i = re.compile('<a title="(.+?)" .+? data-(.+?)="(.+?)"').findall(r)
                for eps, marker, t in i:
                    if '1080p' in eps:
                        quality = '1080p'
                    elif '720p' in eps:
                        quality = '720p'
                    else:
                        quality = 'SD'
                    try:
                        if 'smango' in marker:
                            url = 'https://streamango.to/embed/%s/?b=xumzuWZUSN8' % t
                        sources.append({'source': 'streamango', 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        return
                    try:
                        if 'openload' in marker:
                            url = 'https://openload.co/embed/%s/' % t
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        return
                    try:
                        if 'vcloud' in marker:
                            url = 'https://openload.co/embed/%s/' % t
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        return
                    try:
                        if 'imdb' in marker:
                            url = 'https://videospider.in/getvideo?key=IfntUpFt05WyyQAJ&video_id=%s' % t
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': 'openload', 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        return
                    try:
                        if 'svbackup' in marker:
                            url = t
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except:
                        return
            return sources
        except:
            return


    def resolve(self, url):
        return url

