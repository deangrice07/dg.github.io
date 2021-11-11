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
from fenomscrapers.modules import cleantitle
from fenomscrapers.modules import client
from fenomscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 5
		self.language = ['en']
		self.domains = ['nyaa.si']
		self.base_link = 'https://nyaa.si'
		self.search_link = '/?f=0&c=0_0&q=%s'
		self.min_seeders = 1
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
			year = data['year']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year
			hdlr2 = 'S%d - %d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year

			query = '%s %s' % (title, hdlr)
			query = re.sub(r'(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)
			query2 = '%s %s' % (title, hdlr2)
			query2 = re.sub(r'(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query2)

			urls = []
			url = self.search_link % quote_plus(query)
			url = '%s%s' % (self.base_link, url)
			urls.append(url)
			url2 = self.search_link % quote_plus(query2)
			url2 = '%s%s' % (self.base_link, url2)
			urls.append(url2)
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)
		except:
			source_utils.scraper_error('NYYAA')
			return sources

		for url in urls:
			try:
				r = client.request(url, timeout='5')
				if not r or 'magnet' not in r: return sources
				r = re.sub(r'\n', '', r)
				r = re.sub(r'\t', '', r)
				tbody = client.parseDOM(r, 'tbody')
				rows = client.parseDOM(tbody, 'tr')

				for row in rows:
					links = zip(
									re.findall(r'href\s*=\s*["\'](magnet:[^"\']+)["\']', row, re.DOTALL | re.I),
									re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', row, re.DOTALL),
									[re.findall(r'<td class\s*=\s*["\']text-center["\']>([0-9]+)</td>', row, re.DOTALL)])
					for link in links:
						url = unquote_plus(link[0]).replace('&amp;', '&').replace(' ', '.').split('&tr')[0]
						url = source_utils.strip_non_ascii_and_unprintable(url)
						hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
						name = url.split('&dn=')[1]
						name = source_utils.clean_name(name)

						if hdlr not in name and hdlr2 not in name: continue
						if source_utils.remove_lang(name): continue

						if hdlr in name:
							t = name.split(hdlr)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
						if hdlr2 in name:
							t = name.split(hdlr2)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
						# if cleantitle.get(t) != cleantitle.get(title): continue # Anime title matching is a bitch!
						try:
							seeders = int(link[2][0])
							if self.min_seeders > seeders: continue
						except: seeders = 0

						quality, info = source_utils.get_release_quality(name, url)
						try:
							size = link[1]
							dsize, isize = source_utils._size(size)
							info.insert(0, isize)
						except: dsize = 0
						info = ' | '.join(info)

						sources.append({'provider': 'nyaa', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
													'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('NYAA')
				return sources
		return sources

	def resolve(self, url):
		return url