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

from liptonscrapers.modules import cfscrape
from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import client
from liptonscrapers.modules import debrid
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['scene-rls.com', 'scene-rls.net']
		self.base_link = 'http://scene-rls.net'
		# self.search_link = '/search/%s'
		self.search_link = '/?s=%s'
		self.scraper = cfscrape.create_scraper()


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
				return sources

			hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			try:
				url = self.search_link % urllib.quote_plus(query)
				url = urlparse.urljoin(self.base_link, url)
				# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

				r = self.scraper.get(url).content

				posts = client.parseDOM(r, 'div', attrs={'class': 'post'})

				items = [];
				dupes = []

				for post in posts:
					try:
						u = client.parseDOM(post, "div", attrs={"class": "postContent"})
						u = client.parseDOM(u, "h2")
						u = client.parseDOM(u, 'a', ret='href')
						u = [(i.strip('/').split('/')[-1], i) for i in u]
						items += u
					except:
						source_utils.scraper_error('SCENERLS')
						pass

			except:
				source_utils.scraper_error('SCENERLS')
				pass

			for item in items:
				try:
					name = item[0]
					name = client.replaceHTMLCodes(name)

					t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					tit = name.replace('.', ' ')

					if hdlr not in tit:
						continue

					quality, info = source_utils.get_release_quality(name, item[1])
					info = ' | '.join(info)

					url = item[1]

					if any(x in url for x in ['.rar', '.zip', '.iso']):
						continue

					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')

					host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]

					if not host in hostDict:
						continue

					host = client.replaceHTMLCodes(host)
					host = host.encode('utf-8')

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
									'direct': False, 'debridonly': True})
				except:
					source_utils.scraper_error('SCENERLS')
					pass

			return sources

		except:
			source_utils.scraper_error('SCENERLS')
			return sources


	def resolve(self, url):
		return url
