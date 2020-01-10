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
# Testing @Cy4Root 01-10-2019 movie: Bohemian Rhapsody (2018)

import re,traceback,urllib,urlparse,json,base64,xbmcgui
from liptonscrapers.modules import client,cleantitle,directstream,source_utils
from liptonscrapers.modules import log_utils,cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['portalciyiz.com'] 
        self.base_link = 'https://portalciyiz.com'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Portalciyiz - Exception: \n' + str(failure))
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            title = urldata['title'].replace(':', ' ').lower()
            year = urldata['year']
            search_id = title.lower()
            start_url = urlparse.urljoin(self.base_link, self.search_link % (search_id.replace(' ','+') + '+' + year))
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            html = self.scraper.get(start_url,headers=headers).content
            Links = re.compile('<div class="col-8">.+?<a href="(.+?)" class="baslikust h5">(.+?)"',re.DOTALL).findall(html)
            for link,name in Links:
                if title.lower() in name.lower(): 
                    if year in name:
                        holder = self.scraper.get(link,headers=headers).content
                        Alterjnates = re.compile('<button class="text-capitalize dropdown-item" value="(.+?)"',re.DOTALL).findall(holder)
                        for alt_link in Alterjnates:
                            alt_url = alt_link.split ("e=")[1]
                            valid, host = source_utils.is_host_valid(alt_url, hostDict)
                            if valid:
                                sources.append({'source':host,'quality':'1080p','language': 'en','url':alt_url,'info':[],'direct':False,'debridonly':False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('Portalciyiz - Exception: \n' + str(failure))
            return sources


    def resolve(self, url):
        if 'google' in url and not 'googleapis' in url:
            return directstream.googlepass(url)
        else:
            return url

