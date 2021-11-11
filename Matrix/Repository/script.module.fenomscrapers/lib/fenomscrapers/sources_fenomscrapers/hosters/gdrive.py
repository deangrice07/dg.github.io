# -*- coding: utf-8 -*-
# (updated 11-04-2021)
'''
	Fenomscrapers Project
'''

import re
import requests
try: #Py2
	from urllib import unquote, quote_plus
except ImportError: #Py3
	from urllib.parse import unquote, quote_plus
from fenomscrapers.modules.control import setting as getSetting
from fenomscrapers.modules import source_utils

cloudflare_worker_url = getSetting('gdrive.cloudflare_url').strip()


def getResults(searchTerm):
	url = '{}/searchjson/{}'.format(cloudflare_worker_url, searchTerm)
	if not url.startswith("https://"): url = "https://" + url
	# log_utils.log('query url = %s' % url)
	results = requests.get(url).json()
	return results

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.title_chk = (getSetting('gdrive.title.chk') == 'true')
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
			query = quote_plus(re.sub(r'[^A-Za-z0-9\s\.-]+', '', query))
			if cloudflare_worker_url == '': return sources
			results = getResults(query)
			if not results: return sources
		except:
			source_utils.scraper_error('GDRIVE')
			return sources

		for result in results:
			try:
				link = result["link"]
				name = unquote(link.rsplit("/")[-1])
				if self.title_chk:
					if not source_utils.check_title(title, aliases, name, hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title) # needs a decent rewrite to get this

				quality, info = source_utils.get_release_quality(name_info, link)
				try:
					size = str(result["size_gb"]) + ' GB'
					dsize, isize = source_utils._size(size)
					if isize: info.insert(0, isize)
				except:
					source_utils.scraper_error('GDRIVE')
					dsize = 0
				info = ' | '.join(info)

				sources.append({'provider': 'gdrive', 'source': 'direct', 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': link, 'info': info,  'direct': True, 'debridonly': False, 'size': dsize})
			except:
				source_utils.scraper_error('GDRIVE')
		return sources

	def resolve(self, url):
		return url