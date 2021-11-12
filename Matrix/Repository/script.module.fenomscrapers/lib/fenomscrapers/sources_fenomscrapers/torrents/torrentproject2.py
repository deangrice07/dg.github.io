# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (11-05-2021)
"""
	Fenomscrapers Project
"""

import re
try: #Py2
	from urllib import quote_plus, unquote_plus
except ImportError: #Py3
	from urllib.parse import quote_plus, unquote_plus
from fenomscrapers.modules import client
from fenomscrapers.modules import source_utils
from fenomscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 6
		self.language = ['en']
		self.domains = ['torrentproject2.com']
		self.base_link = 'https://torrentproject2.com'
		self.search_link = '/?t=%s&orderby=seeders'
		self.min_seeders = 1
		self.pack_capable = True
		self.movie = True
		self.tvshow = True

	def sources(self, data, hostDict):
		self.sources = []
		if not data: return self.sources
		try:
			self.title = data['tvshowtitle'].lower() if 'tvshowtitle' in data else data['title'].lower()
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			self.aliases = data['aliases']
			self.year = data['year']
			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else self.year
			self.episode_title = data['title'] if 'tvshowtitle' in data else None

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', query)
			url = ('%s%s' % (self.base_link, self.search_link % quote_plus(query))).replace('+', '-')
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = client.request(url, timeout='5')
			if not r: return self.sources
			links = re.findall(r'<a\s*href\s*=\s*["\'](.+?torrent.html)["\']', r, re.I)
			threads = []
			for link in links:
				threads.append(workers.Thread(self.get_sources, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('TORRENTPROJECT2')
			return self.sources

	def get_sources(self, link):
		try:
			url = '%s%s' % (self.base_link, link)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)
			result = client.request(url, timeout='5')
			if result is None: return
			hash = re.search(r'<a\s*title\s*=\s*["\']hash:(.+?)\s*torrent', result, re.I).group(1)

			name = re.search(r'<title>(.+?)</title>', result, re.I).group(1)
			name = source_utils.clean_name(unquote_plus(name))
			if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year): return
			name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
			if source_utils.remove_lang(name_info): return

			if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
				ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
				if any(re.search(item, name.lower()) for item in ep_strings): return

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
			if url in str(self.sources): return
			try:
				seeders = int(re.search(r'["\']tseeders["\']>\s*([0-9]+|[0-9]+,[0-9]+)\s*<', result, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except:
				source_utils.scraper_error('TORRENTPROJECT2')
				seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'<div id\s*=\s*["\']torrent-size["\']>(.+?)<', result, re.I).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			self.sources.append({'provider': 'torrentproject2', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('TORRENTPROJECT2')

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
		self.items = []
		if not data: return self.sources
		try:
			self.search_series = search_series
			self.total_seasons = total_seasons
			self.bypass_filter = bypass_filter

			self.title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU')
			self.aliases = data['aliases']
			self.imdb = data['imdb']
			self.year = data['year']
			self.season_x = data['season']
			self.season_xx = self.season_x.zfill(2)

			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', self.title)
			queries = [
						self.search_link % quote_plus(query + ' S%s' % self.season_xx),
						self.search_link % quote_plus(query + ' Season %s' % self.season_x)]
			if search_series:
				queries = [
						self.search_link % quote_plus(query + ' Season'),
						self.search_link % quote_plus(query + ' Complete')]
			threads = []
			for url in queries:
				link = ('%s%s' % (self.base_link, url)).replace('+', '-')
				threads.append(workers.Thread(self.get_pack_items, link))
			[i.start() for i in threads]
			[i.join() for i in threads]

			threads2 = []
			for i in self.items:
				threads2.append(workers.Thread(self.get_pack_sources, i))
			[i.start() for i in threads2]
			[i.join() for i in threads2]
			return self.sources
		except:
			source_utils.scraper_error('TORRENTPROJECT2')
			return self.sources

	def get_pack_items(self, url):
		try:
			r = client.request(url, timeout='5')
			if not r: return
			links = re.findall(r'<a\s*href\s*=\s*["\'](.+?torrent.html)["\']', r, re.I)
			for link in links:
				url = '%s%s' % (self.base_link, link)
				self.items.append((url))
			return self.items
		except:
			source_utils.scraper_error('TORRENTPROJECT2')

	def get_pack_sources(self, url):
		try:
			# log_utils.log('url = %s' % str(url))
			result = client.request(url, timeout='5')
			if not result: return
			hash = re.search(r'<a\s*title\s*=\s*["\']hash:(.+?)\s*torrent', result, re.I).group(1)

			name = re.search(r'<title>(.+?)</title>', result, re.I).group(1)
			name = source_utils.clean_name(unquote_plus(name))
			if not self.search_series:
				if not self.bypass_filter:
					if not source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name):
						return
				package = 'season'

			elif self.search_series:
				if not self.bypass_filter:
					valid, last_season = source_utils.filter_show_pack(self.title, self.aliases, self.imdb, self.year, self.season_x, name, self.total_seasons)
					if not valid: return
				else:
					last_season = self.total_seasons
				package = 'show'

			name_info = source_utils.info_from_name(name, self.title, self.year, season=self.season_x, pack=package)
			if source_utils.remove_lang(name_info): return

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
			if url in str(self.sources): return
			try:
				seeders = int(re.search(r'["\']tseeders["\']>\s*([0-9]+|[0-9]+,[0-9]+)\s*<', result, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'<div id\s*=\s*["\']torrent-size["\']>(.+?)<', result, re.I).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			item = {'provider': 'torrentproject2', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
						'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
			if self.search_series: item.update({'last_season': last_season})
			self.sources.append(item)
		except:
			source_utils.scraper_error('TORRENTPROJECT2')

	def resolve(self, url):
		return url