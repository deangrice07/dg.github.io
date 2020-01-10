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
import urllib
import urlparse

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import dom_parser
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['tvbox.ag']
		self.base_link = 'http://tvbox.ag'
		self.search_link = 'http://tvbox.ag/search?q=%s'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			query = self.search_link % urllib.quote_plus(cleantitle.query(title))
			for i in range(3):
				result = self.scraper.get(query).content
				if not result is None:
					break
			t = [title] + [localtitle] + source_utils.aliases_to_array(aliases)
			t = [cleantitle.get(i) for i in set(t) if i]
			items = dom_parser.parse_dom(result, 'div', attrs={'class': 'result'})
			url = None
			for i in items:
				result = re.findall(r'href="([^"]+)">(.*)<', i.content)
				if re.sub('<[^<]+?>', '', cleantitle.get(cleantitle.normalize(result[0][1]))) in t and year in \
						result[0][1]:
					url = result[0][0]
				if not url is None:
					break
			url = url.encode('utf-8')
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			query = self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle))
			for i in range(3):
				result = self.scraper.get(query).content
				if not result is None:
					break
			t = [tvshowtitle] + source_utils.aliases_to_array(aliases)
			t = [cleantitle.get(i) for i in set(t) if i]
			items = dom_parser.parse_dom(result, 'div', attrs={'class': 'result'})
			url = None
			for i in items:
				result = re.findall(r'href="([^"]+)">(.*)<', i.content)
				if re.sub('<[^<]+?>', '', cleantitle.get(cleantitle.normalize(result[0][1]))) in t and year in \
						result[0][1]:
					url = result[0][0]
				if not url is None:
					break
			url = url.encode('utf-8')
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = urlparse.urljoin(self.base_link, url)
			for i in range(3):
				result = self.scraper.get(url).content
				if not result is None:
					break
			title = cleantitle.get(title)
			premiered = re.compile('(\d{4})-(\d{2})-(\d{2})').findall(premiered)[0]
			premiered = '%s/%s/%s' % (premiered[2], premiered[1], premiered[0])
			result = re.findall(r'<h\d>Season\s+%s<\/h\d>(.*?<\/table>)' % season, result)[0]
			result = \
			dom_parser.parse_dom(result, 'a', attrs={'href': re.compile('.*?episode-%s/' % episode)}, req='href')[0]
			url = result.attrs['href']
			url = url.encode('utf-8')
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			url = urlparse.urljoin(self.base_link, url)
			for i in range(3):
				result = self.scraper.get(url).content
				if not result is None:
					break
			links = re.compile('onclick="report\(\'([^\']+)').findall(result)
			for link in links:
				try:
					valid, hoster = source_utils.is_host_valid(link, hostDict)
					if not valid:
						continue
					urls, host, direct = source_utils.check_directstreams(link, hoster)
					if source_utils.limit_hosts() is True and host in str(sources):
						continue
					for x in urls:
						sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'],
						                'direct': direct, 'debridonly': False})
				except:
					pass
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
