# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 11-05-2021)
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


class source:
	def __init__(self):
		self.priority = 5
		self.language = ['en']
		self.domains = ['topnow.se']
		self.base_link = 'http://topnow.se'
		self.search_link = '/index.php?search=%s'
		self.show_link = '/index.php?show=%s'
		self.pack_capable = False
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
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else ('(' + year + ')')

			query = title
			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', query)
			if 'tvshowtitle' in data: url = self.show_link % query.replace(' ', '-')
			else: url = self.search_link % quote_plus(query)
			url = '%s%s' % (self.base_link, url)
			# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)
			r = client.request(url, timeout='5')
			if not r: return sources
			r = r.replace('\r', '').replace('\n', '').replace('\t', '')
			r = client.parseDOM(r, 'div', attrs={'class': 'card'})
			if not r: return sources
		except:
			source_utils.scraper_error('TOPNOW')
			return sources
		for i in r:
			try:
				if 'magnet:' not in i: continue
				name = client.parseDOM(i, 'img', attrs={'class': 'thumbnails'}, ret='alt')[0].replace(u'\xa0', u' ')
				if not source_utils.check_title(title, aliases, name, hdlr.replace('(', '').replace(')', ''), year): continue

				url = re.search(r'href\s*=\s*["\'](magnet:[^"\']+)["\']', i, re.DOTALL | re.I).group(1)
				try: url = unquote_plus(url).decode('utf8').replace('&amp;', '&').replace(' ', '.')
				except: url = unquote_plus(url).replace('&amp;', '&').replace(' ', '.')
				url = re.sub(r'(&tr=.+)&dn=', '&dn=', url) # some links on topnow &tr= before &dn=
				url = url.split('&tr=')[0].replace(' ', '.')
				url = source_utils.strip_non_ascii_and_unprintable(url)
				hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
				release_name = url.split('&dn=')[1]
				release_name = source_utils.clean_name(release_name)
				name_info = source_utils.info_from_name(release_name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info): continue

				seeders = 0 # seeders not available on topnow
				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', i).group(0) # file size is no longer available on topnow's new site
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				sources.append({'provider': 'topnow', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': release_name, 'name_info': name_info,
										'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('TOPNOW')
		return sources

	def resolve(self, url):
		return url