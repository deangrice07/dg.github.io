# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    ExoScrapers Project
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib
import urlparse

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import debrid
from liptonscrapers.modules import source_utils
from liptonscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['torrentdownloads.me', 'torrentsdl1.unblocked.lol']
		self.base_link = 'https://torrentsdl1.unblocked.to/'
		self.search = 'https://www.torrentdownloads.me/rss.xml?new=1&type=search&cid={0}&search={1}'
		self.min_seeders = 1


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			self._sources = []

			if url is None:
				return self._sources

			if debrid.status() is False:
				return self._sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
			self.year = data['year']

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			if 'tvshowtitle' in data:
				url = self.search.format('8', urllib.quote(query))
			else:
				url = self.search.format('4', urllib.quote(query))
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			headers = {'User-Agent': client.agent()}

			_html = client.request(url, headers=headers)

			threads = []
			for i in re.findall(r'<item>(.+?)</item>', _html, re.DOTALL):
				threads.append(workers.Thread(self._get_items, i))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self._sources

		except:
			source_utils.scraper_error('TORRENTDOWNLOADS')
			return self._sources


	def _get_items(self, r):
		try:
			size = re.search(r'<size>([\d]+)</size>', r).groups()[0]
			seeders = re.search(r'<seeders>([\d]+)</seeders>', r).groups()[0]

			_hash = re.search(r'<info_hash>([a-zA-Z0-9]+)</info_hash>', r).groups()[0]
			name = re.search(r'<title>(.+?)</title>', r).groups()[0]

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (_hash.upper(), urllib.quote_plus(name))

			if any(x in url.lower() for x in ['french', 'italian', 'spanish', 'truefrench', 'dublado', 'dubbed']):
					continue

			t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '').replace('&', 'and')
			t = name.split(self.hdlr)[0]
			if cleantitle.get(t) != cleantitle.get(self.title):
				return

			if self.hdlr not in name:
				raise Exception()

			quality, info = source_utils.get_release_quality(name, name)

			try:
				div = 1000 ** 3
				size = float(size) / div
				size = '%.2f GB' % size
				info.append(size)
			except:
				pass

			info = ' | '.join(info)

			if seeders > self.min_seeders:
				self._sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
													'info': info, 'direct': False, 'debridonly': True})
		except:
			source_utils.scraper_error('TORRENTDOWNLOADS')
			pass


	def resolve(self, url):
		return url
