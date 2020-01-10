# -*- coding: UTF-8 -*-

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

import json
import traceback
import urllib
import urlparse

from liptonscrapers.modules import cleantitle
from liptonscrapers.modules import control
from liptonscrapers.modules import log_utils
from liptonscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru']
		self.domains = []

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			return urllib.urlencode({'imdb': imdb, 'title': title, 'localtitle': localtitle, 'year': year})
		except:
			failure = traceback.format_exc()
			log_utils.log('Library - Exception: \n' + str(failure))
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			return urllib.urlencode(
				{'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle,
				 'year': year})
		except:
			failure = traceback.format_exc()
			log_utils.log('Library - Exception: \n' + str(failure))
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return

			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url.update({'premiered': premiered, 'season': season, 'episode': episode})
			return urllib.urlencode(url)
		except:
			failure = traceback.format_exc()
			log_utils.log('Library - Exception: \n' + str(failure))
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []

		try:
			if url is None:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			content_type = 'episode' if 'tvshowtitle' in data else 'movie'

			years = (data['year'], str(int(data['year']) + 1), str(int(data['year']) - 1))

			if content_type == 'movie':
				title = cleantitle.get(data['title'])
				localtitle = cleantitle.get(data['localtitle'])
				ids = [data['imdb']]

				r = control.jsonrpc(
					'{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties": ["imdbnumber", "title", "originaltitle", "file"]}, "id": 1}' % years)
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']
				if 'movies' in r:
					r = r['movies']
				else:
					return sources

				r = [i for i in r if
				     str(i['imdbnumber']) in ids or title in [cleantitle.get(i['title'].encode('utf-8')),
				                                              cleantitle.get(i['originaltitle'].encode('utf-8'))]]
				r = [i for i in r if not i['file'].encode('utf-8').endswith('.strm')][0]

				r = control.jsonrpc(
					'{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["streamdetails", "file"], "movieid": %s }, "id": 1}' % str(
						r['movieid']))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['moviedetails']
			elif content_type == 'episode':
				title = cleantitle.get(data['tvshowtitle'])
				localtitle = cleantitle.get(data['localtvshowtitle'])
				season, episode = data['season'], data['episode']
				ids = [data['imdb'], data['tvdb']]

				r = control.jsonrpc(
					'{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties": ["imdbnumber", "title"]}, "id": 1}' % years)
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']
				if 'tvshows' in r:
					r = r['tvshows']
				else:
					return sources

				r = [i for i in r if
				     str(i['imdbnumber']) in ids or title in [cleantitle.get(i['title'].encode('utf-8')),
				                                              cleantitle.get(i['originaltitle'].encode('utf-8'))]][0]

				r = control.jsonrpc(
					'{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["file"], "tvshowid": %s }, "id": 1}' % (
						str(season), str(episode), str(r['tvshowid'])))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['episodes']

				r = [i for i in r if not i['file'].encode('utf-8').endswith('.strm')][0]

				r = control.jsonrpc(
					'{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["streamdetails", "file"], "episodeid": %s }, "id": 1}' % str(
						r['episodeid']))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['episodedetails']

			url = r['file'].encode('utf-8')

			try:
				quality = int(r['streamdetails']['video'][0]['width'])
			except:
				quality = -1

			quality = source_utils.label_to_quality(quality)

			info = []
			try:
				f = control.openFile(url);
				s = f.size();
				f.close()
				s = '%.2f GB' % (float(s) / 1024 / 1024 / 1024)
				info.append(s)
			except:
				pass
			try:
				e = urlparse.urlparse(url).path.split('.')[-1].upper()
				info.append(e)
			except:
				pass
			info = ' | '.join(info)
			info = info.encode('utf-8')

			sources.append(
				{'source': '0', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'local': True,
				 'direct': True, 'debridonly': False})

			return sources
		except:
			failure = traceback.format_exc()
			log_utils.log('Library - Exception: \n' + str(failure))
			return sources

	def resolve(self, url):
		return url
