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
# Testing @Cy4Root 01-10-2019 movie: It Chapter 2 

import re,urllib,urlparse,base64
from liptonscrapers.modules import cleantitle,client,proxy,source_utils,cfscrape


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['putlockers.plus', 'putlockers.fm', 'putlockers.ws', 'putlockers.gs']
		self.base_link = 'http://putlockers.plus'
		self.search_link = '/search-movies/%s.html'
		self.scraper = cfscrape.create_scraper()


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			find = cleantitle.geturl(title)
			query = find.replace('-','+')
			url = self.base_link + self.search_link % query
			r = self.scraper.get(url).content
			match = re.compile('<a href="http://putlockers.plus/watch/(.+?)-' + find + '.html"').findall(r)
			for url_id in match:
				url = 'http://putlockers.plus/watch/' + url_id + '-' + find + '.html'
				r = self.scraper.get(url).content
				return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			url = url.replace('-','+')
			return url
		except:
			return
 
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			query = url + '+season+' + season
			find = query.replace('+','-')
			url = self.base_link + self.search_link % query
			r = self.scraper.get(url).content
			match = re.compile('<a href="http://putlockers.plus/watch/(.+?)-' + find + '.html"').findall(r)
			for url_id in match:
				url = 'http://putlockers.plus/watch/' + url_id + '-' + find + '.html'
				r = self.scraper.get(url).content
				match = re.compile('<a class="episode episode_series_link" href="(.+?)">' + episode + '</a>').findall(r)
				for url in match:
					return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = self.scraper.get(url).content
			try:
				match = re.compile('<p class="server_version"><img src="http://putlockers.plus/themes/movies/img/icon/server/(.+?).png" width="16" height="16" /> <a href="(.+?)">').findall(r)
				for host, url in match: 
					if host == 'openload': pass 
					else:
						quality = source_utils.check_url(url)
						valid, host = source_utils.is_host_valid(host, hostDict)
						if valid:
						    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
			except:
				return
		except Exception:
			return
		return sources


	def resolve(self, url):
		r = self.scraper.get(url).content
		match = re.compile('decode\("(.+?)"').findall(r)
		for info in match:
			info = base64.b64decode(info)
			match = re.compile('src="(.+?)"').findall(info)
			for url in match:
				return url

