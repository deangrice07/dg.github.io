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
from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['azm.to', 'azmovie.to']
		self.base_link = 'https://azm.to'
		self.search_link = '/watch.php?title=%s'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title).replace('-', '+').replace(':', '%3A+')
			url = self.base_link + self.search_link % title
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			r = self.scraper.get(url).content
			u = client.parseDOM(r, "ul", attrs={"id": "serverul"})

			for t in u:
				u = client.parseDOM(t, 'a', ret='href')
				for url in u:
					quality = source_utils.check_url(url)
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid or 'getlink' in url:
						sources.append(
							{'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
							 'debridonly': False})
				return sources
		except:
			return

	def resolve(self, url):
		return url
