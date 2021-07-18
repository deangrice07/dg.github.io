# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from json import loads as jsloads
import re
from urllib.parse import urlencode, parse_qsl, urlparse, urlsplit
from resources.lib.modules import client
from resources.lib.modules import trakt
from resources.lib.modules import workers

self.trakt_link = 'https://api.trakt.tv'
# self.trakt_user = control.setting('trakt.user').strip()
self.lang = control.apiLanguage()['trakt']

self.traktlist_link = 'https://api.trakt.tv/users/%s/lists/%s/items'
self.traktlists_link = 'https://api.trakt.tv/users/me/lists'
self.traktlikedlists_link = 'https://api.trakt.tv/users/likes/lists?limit=1000000'
self.traktcollection_link = 'https://api.trakt.tv/users/me/collection/movies'
self.traktwatchlist_link = 'https://api.trakt.tv/users/me/watchlist/movies'
self.trakthistory_link = 'https://api.trakt.tv/users/me/history/movies?limit=%d&page=1' % self.count
self.traktunfinished_link = 'https://api.trakt.tv/sync/playback/movies'

self.traktanticipated_link = 'https://api.trakt.tv/movies/anticipated?limit=%d&page=1' % self.count
self.traktrecommendations_link = 'https://api.trakt.tv/recommendations/movies?limit=%d' % self.count
self.trakttrending_link = 'https://api.trakt.tv/movies/trending?limit=40&page=1'
self.traktboxoffice_link = 'https://api.trakt.tv/movies/boxoffice?limit=40&page=1'
self.traktpopular_link = 'https://api.trakt.tv/movies/popular?limit=40&page=1'

# https://api.trakt.tv/users/id/collection/type


def trakt_list(self, url, user):
	try:
		q = dict(parse_qsl(urlsplit(url).query))
		q.update({'extended': 'full'})
		q = (urlencode(q)).replace('%2C', ',')
		u = url.replace('?' + urlparse(url).query, '') + '?' + q
		result = trakt.getTraktAsJson(u)
		items = []
		for i in result:
			try:
				movie = i['movie']
				try: movie['progress'] = max(0, min(1, i['progress'] / 100.0))
				except: pass
				items.append(movie)
			except: pass
		if len(items) == 0:
			items = result
	except: return
	try:
		q = dict(parse_qsl(urlsplit(url).query))
		if not int(q['limit']) == len(items): raise Exception()
		q.update({'page': str(int(q['page']) + 1)})
		q = (urlencode(q)).replace('%2C', ',')
		next = url.replace('?' + urlparse(url).query, '') + '?' + q
		next = next.encode('utf-8')
	except:
		next = ''
	for item in items:
		try:
			title = item.get('title')
			premiered = str(item.get('released', '')) if item.get('released') else ''
			year = str(item.get('year', '')) if item.get('year') else ''
			if not year:
				try: year = premiered[:4]
				except: year = ''
			# if int(year) > int((self.date_time).strftime('%Y')): raise Exception()

			try: progress = item['progress']
			except: progress = None

			ids = item.get('ids', {})
			imdb = str(ids.get('imdb', '')) if ids.get('imdb') else ''
			tmdb = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''

			genre = []
			for x in item['genres']:
				genre.append(x.title())
			if genre == []: genre = 'NA'

			duration = str(item.get('runtime', ''))
			rating = str(item.get('rating', ''))
			votes = str(item.get('votes', ''))
			mpaa = item.get('certification', '')
			plot = item.get('overview')
			# tagline = item.get('tagline', '')
			tagline = ''
			self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'genre': genre, 'duration': duration,
										'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'tagline': tagline, 'imdb': imdb, 'tmdb': tmdb,
										'tvdb': '', 'poster': '', 'fanart': '', 'next': next, 'progress': progress})
		except:
			pass
	return self.list

def trakt_user_list(self, url, user):
	try:
		result = trakt.getTrakt(url)
		items = jsloads(result)
	except: pass
	for item in items:
		try:
			try: name = item['list']['name']
			except: name = item['name']
			name = client.replaceHTMLCodes(name)
			try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
			except: url = ('me', item['ids']['slug'])
			url = self.traktlist_link % url
			self.list.append({'name': name, 'url': url, 'context': url})
		except:
			pass
	self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
	return self.list