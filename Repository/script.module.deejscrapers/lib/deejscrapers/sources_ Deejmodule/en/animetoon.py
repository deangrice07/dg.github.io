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
import re

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.genre_filter = ['animation', 'anime']
		self.domains = ['animetoon.org', 'animetoon.tv']
		self.base_link = 'http://www.animetoon.org'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = '%s-%s' % (title, year)
			url = self.base_link + '/' + url
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			if season == '1':
				url = self.base_link + '/' + url + '-episode-' + episode
			else:
				url = self.base_link + '/' + url + '-season-' + season + '-episode-' + episode
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			r = self.scraper.get(url).content
			match = re.compile('<div><iframe src="(.+?)"').findall(r)
			for url in match:
				host = url.split('//')[1].replace('www.', '')
				host = host.split('/')[0].split('.')[0].title()
				quality = source_utils.check_sd_url(url)
				r = self.scraper.get(url).content
				if 'http' in url:
					match = re.compile("url: '(.+?)',").findall(r)
				else:
					match = re.compile('file: "(.+?)",').findall(r)
				for url in match:
					sources.append(
						{'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
						 'debridonly': False})
		except:
			return
		return sources

	def resolve(self, url):
		return url
