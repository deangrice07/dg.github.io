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
import traceback

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import log_utils
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['1putlocker.io']
		self.base_link = 'https://www15.1putlocker.io'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = self.base_link + '/%s/' % title
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			tvshowtitle = url
			url = self.base_link + '/episode/%s-season-%s-episode-%s/' % (tvshowtitle, season, episode)
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			r = self.scraper.get(url).content
			try:
				match = re.compile('<iframe src="(.+?)"').findall(r)
				for url in match:
					quality = source_utils.check_url(url)
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						sources.append(
							{'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
							 'debridonly': False})
			except:
				return
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return
		return sources

	def resolve(self, url):
		return url
