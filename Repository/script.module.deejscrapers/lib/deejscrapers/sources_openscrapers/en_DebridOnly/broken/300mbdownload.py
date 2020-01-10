# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project
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


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['300mbdownload.mobi']
		self.base_link = 'https://www.300mbdownload.mobi'
		self.search_link = '/search/%s/feed/rss2/'
	# self.search_link = '/?s=%s' #rss2 seems down in which a re-write to parse will be needed

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
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				raise Exception()

			hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			html = client.request(url)

			posts = client.parseDOM(html, 'item')

			items = []
			for post in posts:
				try:
					t = client.parseDOM(post, 'title')[0]
					u = client.parseDOM(post, 'a', ret='href')
					s = re.search('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', post)
					s = s.groups()[0] if s else '0'
					items += [(t, i, s) for i in u]
				except:
					source_utils.scraper_error('300MBDOWNLOAD')
					pass

			for item in items:
				try:
					name = item[0]
					name = client.replaceHTMLCodes(name)

					t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if self.hdlr not in name:
						continue

					url = item[1]
					if any(x in url for x in ['.rar', '.zip', '.iso']):
						continue

					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')

					if url in str(sources):
						continue

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					host = client.replaceHTMLCodes(host)
					host = host.encode('utf-8')

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', item[2])[-1]
						div = 1 if size.endswith(('GB', 'GiB')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
						size = '%.2f GB' % size
						info.append(size)
					except:
						pass

					fileType = source_utils.getFileType(name)
					info.append(fileType)
					info = ' | '.join(info) if fileType else info[0]

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
					                'info': info, 'direct': False, 'debridonly': True})
				except:
					source_utils.scraper_error('300MBDOWNLOAD')
					pass

			return sources
		except:
			source_utils.scraper_error('300MBDOWNLOAD')
			return

	def resolve(self, url):
		return url
