# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (11-05-2021)
"""
	Fenomscrapers Project
"""

import re
try: #Py2
	from urllib import quote_plus
except ImportError: #Py3
	from urllib.parse import quote_plus
from fenomscrapers.modules import client
from fenomscrapers.modules import source_utils
from fenomscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 3
		self.language = ['en']
		self.domains = ['bt4g.org']
		self.base_link = 'https://bt4g.org'
		self.search_link = '/movie/search/%s/byseeders/1' # site option "video" adds "/movie/" to url
		self.min_seeders = 0
		self.pack_capable = True
		self.movie = True
		self.tvshow = True

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		try:
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			aliases = data['aliases']
			episode_title = data['title'] if 'tvshowtitle' in data else None
			year = data['year']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year

			query = '%s %s' % (title, hdlr)
			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', query)
			url = self.search_link % quote_plus(query)
			url = '%s%s' % (self.base_link, url)
			# log_utils.log('url = %s' % url)
			r = client.request(url, timeout='5')
			if not r or 'did not match any documents' in r: return sources
			r = r.replace('&nbsp;', ' ')
			r = client.parseDOM(r, 'div', attrs={'class': 'col s12'})
			posts = client.parseDOM(r, 'div')[1:]
			posts = [i for i in posts if 'magnet/' in i]
		except:
			source_utils.scraper_error('BT4G')
			return sources
		for post in posts:
			try:
				name = client.parseDOM(post, 'a', ret='title')[0]
				name = source_utils.clean_name(name)
				if not source_utils.check_title(title, aliases, name, hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info): continue

				hash = client.parseDOM(post, 'a', ret='href')[0].split('magnet/')[1]
				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

				if not episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
					ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
					if any(re.search(item, name.lower()) for item in ep_strings): continue
				try:
					seeders = int(client.parseDOM(post, 'b', attrs={'id': 'seeders'})[0].replace(',', ''))
					if self.min_seeders > seeders: return
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', post).group(0) #lot of combo S01E01-E08 so parse episode item for size instead, it's closer
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				sources.append({'provider': 'bt4g', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('BT4G')
				return sources
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
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
				link = '%s%s' % (self.base_link, url)
				threads.append(workers.Thread(self.get_sources_packs, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('BTDB')
			return self.sources

	def get_sources_packs(self, link):
		# log_utils.log('link = %s' % str(link))
		r = client.request(link, timeout='5')
		if not r or 'did not match any documents' in r: return
		r = r.replace('&nbsp;', ' ')
		r = client.parseDOM(r, 'div', attrs={'class': 'col s12'})
		posts = client.parseDOM(r, 'div')[1:]
		posts = [i for i in posts if 'magnet/' in i]
		for post in posts:
			try:
				name = client.parseDOM(post, 'a', ret='title')[0]
				name = source_utils.clean_name(name)

				if not self.search_series:
					if not self.bypass_filter:
						if not source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name):
							continue
					package = 'season'

				elif self.search_series:
					if not self.bypass_filter:
						valid, last_season = source_utils.filter_show_pack(self.title, self.aliases, self.imdb, self.year, self.season_x, name, self.total_seasons)
						if not valid: continue
					else:
						last_season = self.total_seasons
					package = 'show'

				name_info = source_utils.info_from_name(name, self.title, self.year, season=self.season_x, pack=package)
				if source_utils.remove_lang(name_info): continue

				hash = client.parseDOM(post, 'a', ret='href')[0].split('magnet/')[1]
				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
				try:
					seeders = int(client.parseDOM(post, 'b', attrs={'id': 'seeders'})[0].replace(',', ''))
					if self.min_seeders > seeders: return
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'<b\s*class\s*=\s*["\']cpill.+?-pill["\']>(.+?)</b>', post, re.I).group(1)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				item = {'provider': 'bt4g', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if self.search_series: item.update({'last_season': last_season})
				self.sources.append(item)
			except:
				source_utils.scraper_error('BT4G')

	def resolve(self, url):
		return url