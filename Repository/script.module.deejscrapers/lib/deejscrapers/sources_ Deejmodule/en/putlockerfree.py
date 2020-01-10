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


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['putlockerfree.info']
		self.base_link = 'https://putlockerfree.info'

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			tvshowtitle = cleantitle.geturl(tvshowtitle)
			url = tvshowtitle
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			http = self.base_link + '/tv_series/%s-season-%s/' % (url, season)
			url = http + 'watching.html/'
			url = 'url="' + url + '"&episode="' + episode + '"'
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			match = re.compile('url="(.+?)"&episode="(.+?)"').findall(url)
			for url, episode in match:
				url = url
				episode = episode
				r = client.request(url)
				try:
					match = re.compile('<a title="Episode ' + episode + '.+?" data-openload="(.+?)"').findall(r)
					for url in match:
						if '2160' in url:
							quality = '4K'
						elif '1080' in url:
							quality = '1080p'
						elif '720' in url:
							quality = 'HD'
						elif '480' in url:
							quality = 'SD'
						else:
							quality = 'SD'
						url = url
						sources.append({
							'source': 'Openload.co',
							'quality': quality,
							'language': 'en',
							'url': url,
							'direct': False,
							'debridonly': False
						})
				except:
					return
		except Exception:
			return
		return sources

	def resolve(self, url):
		return url
