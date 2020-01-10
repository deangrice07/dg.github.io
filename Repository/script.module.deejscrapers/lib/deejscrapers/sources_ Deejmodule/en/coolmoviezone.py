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

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['coolmoviezone.xyz']
		self.base_link = 'https://coolmoviezone.xyz'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title)
			url = self.base_link + '/%s-%s' % (mtitle, year)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			r = client.request(url)
			match = re.compile('<td align="center"><strong><a href="(.+?)"').findall(r)
			for url in match:
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:
					quality, info = source_utils.get_release_quality(url, url)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except Exception:
			return sources

	def resolve(self, url):
		return url
