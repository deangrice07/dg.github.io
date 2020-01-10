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
		self.domains = ['limetorrents.info']
		self.base_link = 'https://www.limetorrents.info'
		self.tvsearch = 'https://www.limetorrents.info/search/tv/{0}/1/'
		self.moviesearch = 'https://www.limetorrents.info/search/movies/{0}/1/'


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
			self.items = []

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

			urls = []
			if 'tvshowtitle' in data:
				url = self.tvsearch.format(urllib.quote(query))
			else:
				url = self.moviesearch.format(urllib.quote(query))
			urls.append(url)

			url2 = url.replace('/1/', '/2/')
			urls.append(url2)
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self._get_items, url))
			[i.start() for i in threads]
			[i.join() for i in threads]

			threads2 = []
			for i in self.items:
				threads2.append(workers.Thread(self._get_sources, i))
			[i.start() for i in threads2]
			[i.join() for i in threads2]
			return self._sources

		except:
			source_utils.scraper_error('LIMETORRENTS')
			return self._sources


	def _get_items(self, url):
		try:
			headers = {'User-Agent': client.agent()}
			r = client.request(url, headers=headers)

			posts = client.parseDOM(r, 'table', attrs={'class': 'table2'})[0]
			posts = client.parseDOM(posts, 'tr')

			for post in posts:
				data = client.parseDOM(post, 'a', ret='href')[1]
				if '/search/' in data:
					continue

				# Remove non-ASCII characters...freakin limetorrents
				try:
					data = data.encode('ascii', 'ignore')
				except:
					pass

				# some broken links with withespace
				data = re.sub('\s', '', data).strip()

				link = urlparse.urljoin(self.base_link, data)

				name = client.parseDOM(post, 'a')[1]

				t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '').replace('&', 'and')
				if cleantitle.get(t) != cleantitle.get(self.title):
					continue

				if self.hdlr not in name:
					continue

				try:
					size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
					div = 1 if size.endswith('GB') else 1024
					size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
					size = '%.2f GB' % size
				except:
					size = '0'
					pass

				self.items.append((name, link, size))

			return self.items

		except:
			source_utils.scraper_error('LIMETORRENTS')
			return self.items


	def _get_sources(self, item):
		try:
			name = item[0]

			quality, info = source_utils.get_release_quality(name, name)

			info.append(item[2]) # if item[2] != '0'
			info = ' | '.join(info)

			data = client.request(item[1])
			if data is None:
				return

			try:
				url = re.search('''href=["'](magnet:\?[^"']+)''', data).groups()[0]
			except:
				return

			if any(x in url.lower() for x in ['french', 'italian', 'spanish', 'truefrench', 'dublado', 'dubbed']):
				return

			self._sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True})

		except:
			source_utils.scraper_error('LIMETORRENTS')
			pass


	def resolve(self, url):
		return url
