# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime, timedelta
from json import loads as jsloads
import re
from urllib.parse import urlparse
from resources.lib.database import cache, metacache, fanarttv_cache
from resources.lib.indexers import fanarttv
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import trakt


class Movies:
	def __init__(self):
		self.count = 40
		self.list = []
		self.meta = []
		self.date_time = datetime.now()
		self.lang = control.apiLanguage()['trakt']
		self.enable_fanarttv = control.setting('enable.fanarttv') == 'true'

		self.imdb_user = control.setting('imdb.user').replace('ur', '')
		self.tmdb_key = control.setting('tmdb.api.key')
		if not self.tmdb_key:
			self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
		self.user = str(self.imdb_user) + str(self.tmdb_key)

		self.tmdb_poster = 'https://image.tmdb.org/t/p/w342'
		self.tmdb_fanart = 'https://image.tmdb.org/t/p/w1280'
		self.tmdb_info_link = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,release_dates,external_ids' % ('%s', self.tmdb_key, self.lang)
																	# other	"append_to_response"options		alternative_titles,videos,images
		self.tmdb_art_link = 'https://api.themoviedb.org/3/movie/%s/images?api_key=%s&include_image_language=en,%s,null' % ('%s', self.tmdb_key, self.lang)


	def imdb_list(self, url, isRatinglink=False):
		list = []
		try:
			for i in re.findall(r'date\[(\d+)\]', url):
				url = url.replace('date[%s]' % i, (self.date_time - timedelta(days=int(i))).strftime('%Y-%m-%d'))
			def imdb_watchlist_id(url):
				return client.parseDOM(client.request(url), 'meta', ret='content', attrs = {'property': 'pageId'})[0]
			if url == self.imdbwatchlist_link:
				url = cache.get(imdb_watchlist_id, 8640, url)
				# url = self.imdblist_link % url
				url = self.imdbwatchlist2_link % url
			result = client.request(url)
			result = result.replace('\n', ' ')
			items = client.parseDOM(result, 'div', attrs = {'class': '.+? lister-item'}) + client.parseDOM(result, 'div', attrs = {'class': 'lister-item .+?'})
			items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
		except:
			log_utils.error()
			return

		next = ''
		try:
			# HTML syntax error, " directly followed by attribute name. Insert space in between. parseDOM can otherwise not handle it.
			result = result.replace('"class="lister-page-next', '" class="lister-page-next')
			next = client.parseDOM(result, 'a', ret='href', attrs = {'class': '.*?lister-page-next.*?'})
			if len(next) == 0:
				next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
				next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
				next = [i[0] for i in next if 'Next' in i[1]]
			next = url.replace(urlparse(url).query, urlparse(next[0]).query)
			next = client.replaceHTMLCodes(next)
		except: next = ''
		for item in items:
			try:
				title = client.replaceHTMLCodes(client.parseDOM(item, 'a')[1])
				year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
				try: year = re.findall(r'(\d{4})', year[0])[0]
				except: continue
				if int(year) > int((self.date_time).strftime('%Y')): continue
				try: show = '–'.decode('utf-8') in str(year).decode('utf-8') or '-'.decode('utf-8') in str(year).decode('utf-8') # check with Matrix
				except: show = False
				if show or ('Episode:' in item): raise Exception() # Some lists contain TV shows.

				try: genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})[0]
				except: genre = ''
				genre = ' / '.join([i.strip() for i in genre.split(',')])
				genre = client.replaceHTMLCodes(genre)

				try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
				except: mpaa = ''
				if isRatinglink and 'Short' not in genre:
					if mpaa in ('TV-Y', 'TV-Y7', 'TV-G', 'TV-PG', 'TV-13', 'TV-14', 'TV-MA'):
						raise Exception()
				if mpaa == '' or mpaa == 'NOT_RATED': mpaa = ''
				mpaa = mpaa.replace('_', '-')
				mpaa = client.replaceHTMLCodes(mpaa)

				imdb = client.parseDOM(item, 'a', ret='href')[0]
				imdb = re.findall(r'(tt\d*)', imdb)[0]

				try: # parseDOM cannot handle elements without a closing tag.
					from bs4 import BeautifulSoup
					html = BeautifulSoup(item, "html.parser")
					poster = html.find_all('img')[0]['loadlate']
				except: poster = ''

				if '/nopicture/' in poster: poster = ''
				if poster:
					poster = re.sub(r'(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
					poster = client.replaceHTMLCodes(poster)

				try: duration = re.findall(r'(\d+?) min(?:s|)', item)[-1]
				except: duration = ''

				rating = ''
				try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
				except:
					try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
					except:
						try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
						except: pass
				if rating == '-': rating = ''
				if not rating:
					try:
						rating = client.parseDOM(item, 'span', attrs = {'class': 'ipl-rating-star__rating'})[0]
						if rating == '-': rating = ''
					except: pass
				rating = client.replaceHTMLCodes(rating)

				votes = ''
				try: votes = client.parseDOM(item, 'span', attrs = {'name': 'nv'})[0]
				except:
					try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
					except:
						try: votes = re.findall(r'\((.+?) vote(?:s|)\)', votes)[0]
						except: pass
				votes = client.replaceHTMLCodes(votes)

				try: director = re.findall(r'Director(?:s|):(.+?)(?:\||</div>)', item)[0]
				except: director = ''
				director = client.parseDOM(director, 'a')
				director = ' / '.join(director)
				director = client.replaceHTMLCodes(director)

				plot = ''
				try: plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
				except:
					try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
					except: pass
				plot = plot.rsplit('<span>', 1)[0].strip()
				plot = re.sub(r'<.+?>|</.+?>', '', plot)
				if not plot:
					try:
						plot = client.parseDOM(item, 'div', attrs = {'class': 'lister-item-content'})[0] # not sure on this, check html
						plot = re.sub(r'<p\s*class="">', '<p class="plot_">', plot)
						plot = client.parseDOM(plot, 'p', attrs = {'class': 'plot_'})[0]
						plot = re.sub(r'<.+?>|</.+?>', '', plot)
					except: pass
				plot = client.cleanHTML(plot)

				values = {}
				values = {'content': 'movie', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered,
						'studio': '', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa,
						'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'code': tmdb,
						'imdb': imdb, 'tmdb': tmdb, 'tvdb': '', 'poster': poster, 'poster2': '', 'poster3': '', 'banner': '',
						'fanart': '', 'fanart2': '', 'fanart3': '', 'clearlogo': '', 'clearart': '', 'landscape': '',
						'metacache': False, 'next': next}
				meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '', 'lang': self.lang, 'user': self.tmdb_key, 'item': values}
				if self.enable_fanarttv:
					extended_art = fanarttv_cache.get(fanarttv.get_movie_art, 168, imdb, tmdb)
					if extended_art:
						values.update(extended_art)
						meta.update(values)

				values = dict((k, v) for k, v in iter(values.items()) if v is not None and v != '')
				self.list.append(values)

				if 'next' in meta.get('item'): del meta['item']['next'] # next can not exist in metacache
				self.meta.append(meta)
				self.meta = [i for i in self.meta if i.get('tmdb')] # without this ui removed missing tmdb but it still writes these cases to metacache?
				metacache.insert(self.meta) # don't insert until cleaned up and can also be fetched.
			except:
				log_utils.error()
		return self.list

	def imdb_person_list(self, url):
		list = []
		try:
			result = client.request(url)
			items = client.parseDOM(result, 'div', attrs = {'class': '.+?etail'})
		except:
			log_utils.error()
			return
		for item in items:
			try:
				name = client.parseDOM(item, 'img', ret='alt')[0]
				# name = name.encode('utf-8')
				url = client.parseDOM(item, 'a', ret='href')[0]
				url = re.findall(r'(nm\d*)', url, re.I)[0]
				url = self.person_link % url
				url = client.replaceHTMLCodes(url)
				image = client.parseDOM(item, 'img', ret='src')[0]
				image = re.sub(r'(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
				image = client.replaceHTMLCodes(image)
				list.append({'name': name, 'url': url, 'image': image})
			except:
				log_utils.error()
		return list

	def imdb_user_list(self, url):
		list = []
		try:
			result = client.request(url) # test .content vs. .text
			items = client.parseDOM(result, 'li', attrs = {'class': 'ipl-zebra-list__item user-list'})
		except: pass

		for item in items:
			try:
				name = client.parseDOM(item, 'a')[0]
				name = client.replaceHTMLCodes(name)
				url = client.parseDOM(item, 'a', ret='href')[0]
				url = url.split('/list/', 1)[-1].strip('/')
				url = self.imdblist_link % url
				url = client.replaceHTMLCodes(url)
				list.append({'name': name, 'url': url, 'context': url, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
			except:
				pass
		list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return self.list

	def super_info(self, i):
		try:
			if self.list[i]['metacache']: return
			imdb = self.list[i].get('imdb', '') ; tmdb = self.list[i].get('tmdb', '')
#### -- Missing id's lookup -- ####
			if not tmdb and imdb:
				try:
					result = cache.get(tmdb_indexer.Movies().IdLookup, 96, imdb)
					tmdb = str(result.get('id', '')) if result.get('id') else ''
				except: tmdb = ''
			if not tmdb and imdb:
				trakt_ids = trakt.IdLookup('imdb', imdb, 'movie')
				if trakt_ids: tmdb = str(trakt_ids.get('tmdb', '')) if trakt_ids.get('tmdb') else ''
			if not tmdb and not imdb:
				try:
					results = trakt.SearchMovie(title=quote_plus(self.list[i]['title']), year=self.list[i]['year'], fields='title', full=False)
					if results[0]['movie']['title'] != self.list[i]['title'] or results[0]['movie']['year'] != self.list[i]['year']: return
					ids = results[0].get('movie', {}).get('ids', {})
					if not tmdb: tmdb = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
					if not imdb: imdb = str(ids.get('imdb', '')) if ids.get('imdb') else ''
				except: pass
#################################
			if not tmdb: return
			movie_meta = cache.get(tmdb_indexer.Movies().get_movie_meta, 96, tmdb)
			if not movie_meta: return
			values = {}
			values.update(movie_meta)
			if 'rating' in self.list[i] and self.list[i]['rating']: del values['rating'] #prefer trakt rating and votes if set
			if 'votes' in self.list[i] and self.list[i]['votes']: del values['votes'] 
			if 'year' in self.list[i] and self.list[i]['year'] != values.get('year'): del values['year'] 
			if not imdb: imdb = values.get('imdb', '')
			if not values.get('imdb'): values['imdb'] = imdb
			if not values.get('tmdb'): values['tmdb'] = tmdb
			if self.lang != 'en':
				try:
					# if self.lang == 'en' or self.lang not in values.get('available_translations', [self.lang]): raise Exception()
					trans_item = trakt.getMovieTranslation(imdb, self.lang, full=True)
					if trans_item:
						if trans_item.get('title'): values['title'] = trans_item.get('title')
						if trans_item.get('overview'): values['plot'] =trans_item.get('overview')
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
			if self.enable_fanarttv:
				extended_art = fanarttv_cache.get(fanarttv.get_movie_art, 168, imdb, tmdb)
				if extended_art: values.update(extended_art)
			values = dict((k, v) for k, v in iter(values.items()) if v is not None and v != '') # remove empty keys so .update() doesn't over-write good meta with empty values.
			self.list[i].update(values)
			meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '', 'lang': self.lang, 'user': self.user, 'item': values}
			self.meta.append(meta)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()


class tvshows:
	def __init__(self):
		self.count = 40
		self.list = []
		self.meta = []
		self.lang = control.apiLanguage()['tvdb']
		self.date_time = datetime.utcnow()
		self.fanart_tv_user = control.setting('fanart.tv.user')
		if not self.fanart_tv_user:
			self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
		self.user = self.fanart_tv_user + str('')
		self.tvdb_key = control.setting('tvdb.api.key')
		# self.tvdb_info_link = 'https://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key.decode('base64'), '%s', self.lang)
		self.tvdb_info_link = 'https://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key, '%s', self.lang)
		self.tvdb_by_imdb = 'https://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
		self.tvdb_by_query = 'https://thetvdb.com/api/GetSeries.php?seriesname=%s'
		self.tvdb_image = 'https://thetvdb.com/banners/'
