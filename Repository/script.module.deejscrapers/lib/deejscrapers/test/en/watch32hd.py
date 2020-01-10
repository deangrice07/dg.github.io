# -*- coding: utf-8 -*-
############################################################################################################################################################################                                                                                                                                       #                                                                                                                                                                          #
#                                                                                                                                                                          #
#    ##     .   **       #########.  ########   #########   ##     ##    #########   #########   #########   #########   #########   ########   #########   ##########     #
#    ##         ##       ##     ##     ###      ##     ##   ###    ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ##     ##     ###      ##     ##   ## #   ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ########      ###      ##     ##   ##  #  ##    #########   ##          ########    #########   ## ######   ########   ########    ##########     #
#    ##         ##       ##            ###      ##     ##   ##   # ##           ##   ##          ##    ##    ##     ##   ##          ##         ##    ##            ##     #
#    ##         ##       ##            ###      ##     ##   ##    ###           ##   ##          ##     ##   ##     ##   ##          ##         ##     ##           ##     #
#    #######    ##       ##     .      ###      #########   ##     ##    #########   ##########  ##      #   ##     ##   ##          ########   ##      #   ##########     #
############################################################################################################################################################################
# Testing @Cy4Root 07-11-2019 movie: 47 meters down 2019
import re,requests,urllib,urlparse
from liptonscrapers.modules import more_sources
from liptonscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en'] 
        self.domains = ['afdah.org', 'putlocker.how', 'watch32hd.co']
        self.base_link = 'https://putlocker.how'
        self.search_link = '/watch?v=%s_%s'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0', 'Referer': self.base_link}
        self.session = requests.Session()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            hostDict = hostDict + hostprDict
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['title']
            year = data['year']
            url = urlparse.urljoin(self.base_link, self.search_link) 
            url = url % (title.replace(':', '').replace(' ','_'),year)
            moviePage = self.session.get(url, headers=self.headers).content
            results = re.compile('var frame_url = "(.+?)"', re.DOTALL | re.M).findall(moviePage)
            if results:
                for url in results:
                    url =  "https:" + url if not url.startswith('http') else url
                    for source in more_sources.more_vidlink(url, hostDict):
                        sources.append(source)
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


