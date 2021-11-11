# -*- coding: utf-8 -*-
# modified by Venom for Fenomscrapers (updated 11-05-2021)
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
		self.priority = 8
		self.language = ['en']
		self.domain = ['ettvcentral.com', 'ettvdl.com']
		self.base_link = 'https://www.ettvcentral.com'
		self.search_link = '/torrents-search.php?search=%s'
		self.min_seeders = 1
		self.pack_capable = False
		self.movie = True
		self.tvshow = True

	def sources(self, data, hostDict):
		self.sources = []
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
			url = self.search_link % quote_plus(query)
			url = '%s%s' % (self.base_link, url)
			# log_utils.log('url = %s' % url)

			r = client.request(url, timeout='10')
			if not r: return self.sources
			links = client.parseDOM(r, "td", attrs={"nowrap": "nowrap"})
			threads = []
			for link in links:
				threads.append(workers.Thread(self.get_sources, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('ETTV')
			return self.sources

	def get_sources(self, link):
		try:
			url = '%s%s' % (self.base_link, re.search(r'href\s*=\s*["\'](.+?)["\']', link, re.I).group(1))
			result = client.request(url, timeout='10')
			if not result or 'magnet' not in result: return
			url = re.search(r'href\s*=\s*["\'](magnet:[^"\']+)["\']', result, re.I).group(1)
			url = unquote_plus(url).replace('&amp;', '&').replace(' ', '.').split('&xl=')[0]
			url = url.replace('&amp;', '&') # some links on ettv dbl "&amp;"
			url = source_utils.strip_non_ascii_and_unprintable(url)
			if url in str(self.sources): return
			hash = re.search(r'btih:(.*?)&', url, re.I).group(1)

			name = url.split('&dn=')[1]
			name = source_utils.clean_name(name)
			if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year): return
			name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
			if source_utils.remove_lang(name_info): return

			if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
				ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
				if any(re.search(item, name.lower()) for item in ep_strings): return
			try:
				seeders = int(re.search(r'>Seeds:.*?["\']>([0-9]+|[0-9]+,[0-9]+)</', result, re.I | re.S).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'>Total Size:.*?>(\d.*?)<', result, re.I | re.S).group(1).strip()
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			self.sources.append({'provider': 'ettv', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('ETTV')

	def resolve(self, url):
		return url