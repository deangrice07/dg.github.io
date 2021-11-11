# -*- coding: utf-8 -*-
# modified by Venom for Fenomscrapers (updated 11-05-2021)
"""
	Fenomscrapers Project
"""

import re
try: #Py2
	from urllib import quote, unquote_plus
except ImportError: #Py3
	from urllib.parse import quote, unquote_plus
from fenomscrapers.modules import client
from fenomscrapers.modules import source_utils
from fenomscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 8
		self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru']
		self.domains = ['1337x.to', '1337x.st', '1337x.ws', '1337x.eu', '1337x.se', '1337x.is'] # all are behind cloudflare except .to
		self.base_link = 'https://1337x.to'
		self.tvsearch = 'https://1337x.to/sort-category-search/%s/TV/size/desc/1/'
		self.moviesearch = 'https://1337x.to/sort-category-search/%s/Movies/size/desc/1/'
		self.min_seeders = 1
		self.pack_capable = False
		self.movie = True
		self.tvshow = True

	def sources(self, data, hostDict):
		self.sources = []
		self.items = []
		if not data: return self.sources
		try:
			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			self.aliases = data['aliases']
			self.episode_title = data['title'] if 'tvshowtitle' in data else None
			self.year = data['year']
			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else self.year

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', query)
			urls = []
			if 'tvshowtitle' in data: urls.append(self.tvsearch % (quote(query)))
			else: urls.append(self.moviesearch % (quote(query)))
			url2 = ''.join(urls).replace('/1/', '/2/')
			urls.append(url2)
			# log_utils.log('urls = %s' % urls)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self.get_items, url))
			[i.start() for i in threads]
			[i.join() for i in threads]

			threads2 = []
			for i in self.items:
				threads2.append(workers.Thread(self.get_sources, i))
			[i.start() for i in threads2]
			[i.join() for i in threads2]
			return self.sources
		except:
			source_utils.scraper_error('1337X')
			return self.sources

	def get_items(self, url):
		try:
			headers = {'User-Agent': client.agent()}
			r = client.request(url, headers=headers, timeout='10')
			if not r or '<tbody' not in r: return
			table = client.parseDOM(r, 'tbody')[0]
			rows = client.parseDOM(table, 'tr')
		except:
			source_utils.scraper_error('1337X')
			return
		for row in rows:
			try:
				link = '%s%s' % (self.base_link, client.parseDOM(row, 'a', ret='href')[1])

				name = source_utils.clean_name(unquote_plus(client.parseDOM(row, 'a')[1]))
				if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year):
					continue
				name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
				if source_utils.remove_lang(name_info): continue

				if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
					ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
					if any(re.search(item, name.lower()) for item in ep_strings): continue
				try:
					seeders = int(client.parseDOM(row, 'td', attrs={'class': 'coll-2 seeds'})[0].replace(',', ''))
					if self.min_seeders > seeders: continue
				except: seeders = 0
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', row).group(0)
					dsize, isize = source_utils._size(size)
				except: isize = '0' ; dsize = 0
				self.items.append((name, name_info, link, isize, dsize, seeders))
			except:
				source_utils.scraper_error('1337X')

	def get_sources(self, item):
		try:
			quality, info = source_utils.get_release_quality(item[1], item[2])
			if item[3] != '0': info.insert(0, item[3])
			info = ' | '.join(info)
			data = client.request(item[2], timeout='10')
			data = client.parseDOM(data, 'a', ret='href')
			if not data: return
			url = [i for i in data if 'magnet:' in i][0]
			url = unquote_plus(url).replace('&amp;', '&').replace(' ', '.').split('&tr')[0]
			url = source_utils.strip_non_ascii_and_unprintable(url)
			hash = re.search(r'btih:(.*?)&', url, re.I).group(1)

			self.sources.append({'provider': '1337x', 'source': 'torrent', 'seeders': item[5], 'hash': hash, 'name': item[0], 'name_info': item[1],
												'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': item[4]})
		except:
			source_utils.scraper_error('1337X')

	def resolve(self, url):
		return url