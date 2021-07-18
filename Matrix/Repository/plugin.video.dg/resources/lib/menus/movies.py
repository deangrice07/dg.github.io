# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime, timedelta
from json import dumps as jsdumps, loads as jsloads
import re
from sys import argv
from urllib.parse import quote_plus, urlencode, parse_qsl, urlparse, urlsplit
from resources.lib.database import cache, metacache
from resources.lib.indexers import tmdb as tmdb_indexer, fanarttv
from resources.lib.modules import cleangenre
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules.playcount import getMovieIndicators, getMovieOverlay
from resources.lib.modules import tools
from resources.lib.modules import trakt
from resources.lib.modules import views
from resources.lib.modules import workers


class Movies:
	def __init__(self, type='movie', notifications=True):
		self.list = []
		self.page_limit = control.setting('page.item.limit')
		self.search_page_limit = control.setting('search.page.limit')
		self.type = type
		self.notifications = notifications
		self.date_time = datetime.now()
		self.today_date = (self.date_time).strftime('%Y-%m-%d')
		self.hidecinema = control.setting('hidecinema') == 'true'

		self.trakt_user = control.setting('trakt.user').strip()
		self.traktCredentials = trakt.getTraktCredentialsInfo()
		self.lang = control.apiLanguage()['trakt']
		self.imdb_user = control.setting('imdb.user').replace('ur', '')
		self.tmdb_key = control.setting('tmdb.api.key')
		if self.tmdb_key == '' or self.tmdb_key is None:
			self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
		self.tmdb_session_id = control.setting('tmdb.session_id')
		# self.user = str(self.imdb_user) + str(self.tmdb_key)
		self.user = str(self.tmdb_key)
		self.disable_fanarttv = control.setting('disable.fanarttv') == 'true'
		self.unairedcolor = control.getColor(control.setting('movie.unaired.identify'))
		self.highlight_color = control.getColor(control.setting('highlight.color'))
		self.tmdb_link = 'https://api.themoviedb.org'
		self.tmdb_popular_link = 'https://api.themoviedb.org/3/movie/popular?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_toprated_link = 'https://api.themoviedb.org/3/movie/top_rated?api_key=%s&page=1'
		self.tmdb_upcoming_link = 'https://api.themoviedb.org/3/movie/upcoming?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_nowplaying_link = 'https://api.themoviedb.org/3/movie/now_playing?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_boxoffice_link = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&language=en-US&region=US&sort_by=revenue.desc&page=1'
		self.tmdb_watchlist_link = 'https://api.themoviedb.org/3/account/{account_id}/watchlist/movies?api_key=%s&session_id=%s&sort_by=created_at.asc&page=1' % ('%s', self.tmdb_session_id)
		self.tmdb_favorites_link = 'https://api.themoviedb.org/3/account/{account_id}/favorite/movies?api_key=%s&session_id=%s&sort_by=created_at.asc&page=1' % ('%s', self.tmdb_session_id)
		self.tmdb_userlists_link = 'https://api.themoviedb.org/3/account/{account_id}/lists?api_key=%s&language=en-US&session_id=%s&page=1' % ('%s', self.tmdb_session_id)
		self.imdb_link = 'https://www.imdb.com'
		self.persons_link = 'https://www.imdb.com/search/name?count=100&name='
		self.personlist_link = 'https://www.imdb.com/search/name?count=100&gender=male,female'
		self.person_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort=year,desc&count=%s&start=1' % ('%s', self.page_limit)
		self.keyword_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&keywords=%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', self.page_limit)
		self.oscars_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&groups=oscar_best_picture_winners&sort=year,desc&count=%s&start=1' % self.page_limit
		self.oscarsnominees_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&groups=oscar_best_picture_nominees&sort=year,desc&count=%s&start=1' % self.page_limit
		self.theaters_link = 'https://www.imdb.com/search/title?title_type=feature&num_votes=500,&release_date=date[90],date[0]&languages=en&sort=release_date,desc&count=%s&start=1' % self.page_limit
		self.year_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', '%s', self.page_limit)
		if self.hidecinema:
			hidecinema_rollback = str(int(control.setting('hidecinema.rollback')) * 30)
			self.mostpopular_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&groups=top_1000&release_date=,date[%s]&sort=moviemeter,asc&count=%s&start=1' % (hidecinema_rollback, self.page_limit )
			self.mostvoted_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=,date[%s]&sort=num_votes,desc&count=%s&start=1' % (hidecinema_rollback, self.page_limit )
			self.featured_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=,date[%s]&sort=moviemeter,asc&count=%s&start=1' % (hidecinema_rollback, self.page_limit )
			self.genre_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[%s]&genres=%s&sort=moviemeter,asc&count=%s&start=1' % (hidecinema_rollback, '%s', self.page_limit)
			self.language_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort=moviemeter,asc&release_date=,date[%s]&count=%s&start=1' % ('%s', hidecinema_rollback, self.page_limit)
			self.certification_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=%s&sort=moviemeter,asc&release_date=,date[%s]&count=%s&start=1' % ('%s', hidecinema_rollback, self.page_limit)
			self.imdbboxoffice_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&release_date=,date[%s]&count=%s&start=1' % (hidecinema_rollback, self.page_limit)
		else:
			self.mostpopular_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&groups=top_1000&sort=moviemeter,asc&count=%s&start=1' % self.page_limit
			self.mostvoted_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&sort=num_votes,desc&count=%s&start=1' % self.page_limit
			self.featured_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&sort=moviemeter,asc&count=%s&start=1' % self.page_limit
			self.genre_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', self.page_limit)
			self.language_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', self.page_limit)
			self.certification_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', self.page_limit)
			self.imdbboxoffice_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&count=%s&start=1' % self.page_limit
		self.imdbwatchlist_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user # only used to get users watchlist ID
		self.imdbwatchlist2_link = 'https://www.imdb.com/list/%s/?view=detail&sort=%s&title_type=movie,short,video,tvShort,tvMovie,tvSpecial&start=1' % ('%s', self.imdb_sort(type='movies.watchlist'))
		self.imdblists_link = 'https://www.imdb.com/user/ur%s/lists?tab=all&sort=mdfd&order=desc&filter=titles' % self.imdb_user
		self.imdblist_link = 'https://www.imdb.com/list/%s/?view=detail&sort=%s&title_type=movie,short,video,tvShort,tvMovie,tvSpecial&start=1' % ('%s', self.imdb_sort())
		self.imdbratings_link = 'https://www.imdb.com/user/ur%s/ratings?sort=your_rating,desc&mode=detail&start=1' % self.imdb_user # IMDb ratings does not take title_type so filter is in imdb_list() function
		self.anime_link = 'https://www.imdb.com/search/keyword?keywords=anime&title_type=movie,tvMovie&sort=moviemeter,asc&count=%s&start=1' % self.page_limit

		self.trakt_link = 'https://api.trakt.tv'
		self.search_link = 'https://api.trakt.tv/search/movie?limit=%s&page=1&query=' % self.search_page_limit
		self.traktlistsearch_link = 'https://api.trakt.tv/search/list?limit=%s&page=1&query=' % self.page_limit
		self.traktlist_link = 'https://api.trakt.tv/users/%s/lists/%s/items/movies'
		self.traktlikedlists_link = 'https://api.trakt.tv/users/likes/lists?limit=1000000'
		self.traktlists_link = 'https://api.trakt.tv/users/me/lists'
		self.traktwatchlist_link = 'https://api.trakt.tv/users/me/watchlist/movies'
		self.traktcollection_link = 'https://api.trakt.tv/users/me/collection/movies' # api collection does not support pagination atm
		self.trakthistory_link = 'https://api.trakt.tv/users/me/history/movies?limit=%s&page=1' % self.page_limit
		self.traktunfinished_link = 'https://api.trakt.tv/sync/playback/movies?limit=40'
		self.traktanticipated_link = 'https://api.trakt.tv/movies/anticipated?limit=%s&page=1' % self.page_limit
		self.trakttrending_link = 'https://api.trakt.tv/movies/trending?limit=%s&page=1' % self.page_limit
		self.traktboxoffice_link = 'https://api.trakt.tv/movies/boxoffice'
		self.traktpopular_link = 'https://api.trakt.tv/movies/popular?limit=%s&page=1' % self.page_limit
		self.traktrecommendations_link = 'https://api.trakt.tv/recommendations/movies?limit=40'

	def get(self, url, idx=True, create_directory=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			try: u = urlparse(url).netloc.lower()
			except: pass
			if u in self.trakt_link and '/users/' in url:
				try:
					isTraktHistory = (url.split('&page=')[0] in self.trakthistory_link)
					if '/users/me/' not in url: raise Exception()
					if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
					self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
					if isTraktHistory:
						for i in range(len(self.list)): self.list[i]['traktHistory'] = True
				except:
					self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)
					if isTraktHistory:
						for i in range(len(self.list)): self.list[i]['traktHistory'] = True
				if idx: self.worker()
				if url == self.traktwatchlist_link: self.sort(type='movies.watchlist')
				else:
					if not isTraktHistory: self.sort()
			elif u in self.trakt_link and self.search_link in url:
				self.list = cache.get(self.trakt_list, 6, url, self.trakt_user)
				if idx: self.worker(level=0)
			elif u in self.trakt_link:
				self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
				if idx: self.worker()
			elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
				isRatinglink = True if self.imdbratings_link in url else False
				self.list = cache.get(self.imdb_list, 0, url, isRatinglink)
				if idx: self.worker()
			elif u in self.imdb_link:
				self.list = cache.get(self.imdb_list, 96, url)
				if idx: self.worker()
			if self.list is None: self.list = []
			if idx and create_directory: self.movieDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32001, message=33049)

	def getTMDb(self, url, idx=True, cached=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			try: u = urlparse(url).netloc.lower()
			except: pass
			if u in self.tmdb_link and '/list/' in url:
				self.list = cache.get(tmdb_indexer.Movies().tmdb_collections_list, 0, url)
				self.sort()
			elif u in self.tmdb_link and not '/list/' in url:
				duration = 168 if cached else 0
				self.list = cache.get(tmdb_indexer.Movies().tmdb_list, duration, url)
			if self.list is None: self.list = []
			if idx: self.movieDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32001, message=33049)

	def unfinished(self, url, idx=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			activity = trakt.getPausedActivity()
			if url == self.traktunfinished_link :
				try:
					if activity > cache.timeout(self.trakt_list, self.traktunfinished_link, self.trakt_user):
						raise Exception()
					self.list = cache.get(self.trakt_list, 720, self.traktunfinished_link , self.trakt_user)
				except:
					self.list = cache.get(self.trakt_list, 0, self.traktunfinished_link , self.trakt_user)
				if idx: self.worker()
			if idx:
				self.list = sorted(self.list, key=lambda k: k['paused_at'], reverse=True)
				self.movieDirectory(self.list, unfinished=True, next=False)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32001, message=33049)

	def sort(self, type='movies'):
		try:
			if not self.list: return
			attribute = int(control.setting('sort.%s.type' % type))
			reverse = int(control.setting('sort.%s.order' % type)) == 1
			if attribute == 0: reverse = False # Sorting Order is not enabled when sort method is "Default"
			if attribute > 0:
				if attribute == 1:
					try: self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['title'].lower()), reverse=reverse)
					except: self.list = sorted(self.list, key=lambda k: k['title'].lower(), reverse=reverse)
				elif attribute == 2: self.list = sorted(self.list, key=lambda k: float(k['rating']), reverse=reverse)
				elif attribute == 3: self.list = sorted(self.list, key=lambda k: int(k['votes'].replace(',', '')), reverse=reverse)
				elif attribute == 4:
					for i in range(len(self.list)):
						if 'premiered' not in self.list[i]: self.list[i]['premiered'] = ''
					self.list = sorted(self.list, key=lambda k: k['premiered'], reverse=reverse)
				elif attribute == 5:
					for i in range(len(self.list)):
						if 'added' not in self.list[i]: self.list[i]['added'] = ''
					self.list = sorted(self.list, key=lambda k: k['added'], reverse=reverse)
				elif attribute == 6:
					for i in range(len(self.list)):
						if 'lastplayed' not in self.list[i]: self.list[i]['lastplayed'] = ''
					self.list = sorted(self.list, key=lambda k: k['lastplayed'], reverse=reverse)
			elif reverse:
				self.list = list(reversed(self.list))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def imdb_sort(self, type='movies'):
		sort = int(control.setting('sort.%s.type' % type))
		imdb_sort = 'list_order'
		if sort == 1: imdb_sort = 'alpha'
		if sort in [2, 3]: imdb_sort = 'user_rating'
		if sort == 4: imdb_sort = 'release_date'
		if sort in [5, 6]: imdb_sort = 'date_added'
		imdb_sort_order = ',asc' if int(control.setting('sort.%s.order' % type)) == 0 else ',desc'
		sort_string = imdb_sort + imdb_sort_order
		return sort_string

	def tmdb_sort(self):
		sort = int(control.setting('sort.movies.type'))
		tmdb_sort = 'original_order'
		if sort == 1: tmdb_sort = 'title'
		if sort in [2, 3]: tmdb_sort = 'vote_average'
		if sort in [4, 5, 6]: tmdb_sort = 'release_date'
		tmdb_sort_order = '.asc' if int(control.setting('sort.movies.order')) == 0 else '.desc'
		sort_string = tmdb_sort + tmdb_sort_order
		return sort_string

	def search(self):
		from resources.lib.menus import navigator
		navigator.Navigator().addDirectoryItem(32603, 'movieSearchnew', 'search.png', 'DefaultAddonsSearch.png', isFolder=False)
		try: from sqlite3 import dbapi2 as database
		except ImportError: from pysqlite2 import dbapi2 as database
		try:
			if not control.existsPath(control.dataPath): control.makeFile(control.dataPath)
			dbcon = database.connect(control.searchFile)
			dbcur = dbcon.cursor()
			dbcur.executescript('''CREATE TABLE IF NOT EXISTS movies (ID Integer PRIMARY KEY AUTOINCREMENT, term);''')
			dbcur.execute('''SELECT * FROM movies ORDER BY ID DESC''')
			dbcur.connection.commit()
			lst = []
			delete_option = False
			for (id, term) in dbcur.fetchall():
				if term not in str(lst):
					delete_option = True
					navigator.Navigator().addDirectoryItem(term, 'movieSearchterm&name=%s' % term, 'search.png', 'DefaultAddonsSearch.png', isSearch=True, table='movies')
					lst += [(term)]
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()
		if delete_option:
			navigator.Navigator().addDirectoryItem(32605, 'cache_clearSearch', 'tools.png', 'DefaultAddonService.png', isFolder=False)
		navigator.Navigator().endDirectory()

	def search_new(self):
		k = control.keyboard('', control.lang(32010))
		k.doModal()
		q = k.getText() if k.isConfirmed() else None
		if not q: return
		try: from sqlite3 import dbapi2 as database
		except ImportError: from pysqlite2 import dbapi2 as database
		try:
			dbcon = database.connect(control.searchFile)
			dbcur = dbcon.cursor()
			dbcur.execute('''INSERT INTO movies VALUES (?,?)''', (None, q))
			dbcur.connection.commit()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()
		url = quote_plus(self.search_link + q)
		control.execute('Container.Update(%s?action=movies&url=%s)' % (argv[0], url))

	def search_term(self, name):
		url = self.search_link + quote_plus(name)
		self.get(url)

	def person(self):
		k = control.keyboard('', control.lang(32010))
		k.doModal()
		q = k.getText().strip() if k.isConfirmed() else None
		if not q: return
		url = self.persons_link + quote_plus(q)
		self.persons(url)

	def persons(self, url):
		if url is None: self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
		else: self.list = cache.get(self.imdb_person_list, 1, url)
		if len(self.list) == 0:
			control.hide()
			control.notification(title=32010, message=33049)
		for i in range(0, len(self.list)):
			self.list[i].update({'icon': 'DefaultActor.png', 'action': 'movies'})
		self.addDirectory(self.list)
		return self.list

	def genres(self):
		genres = [
			('Action', 'action', True), ('Adventure', 'adventure', True), ('Animation', 'animation', True),
			('Biography', 'biography', True), ('Comedy', 'comedy', True), ('Crime', 'crime', True),
			('Documentary', 'documentary', True), ('Drama', 'drama', True), ('Family', 'family', True),
			('Fantasy', 'fantasy', True), ('Film-Noir', 'film-noir', True), ('History', 'history', True),
			('Horror', 'horror', True), ('Music ', 'music', True), ('Musical', 'musical', True),
			('Mystery', 'mystery', True), ('Romance', 'romance', True), ('Science Fiction', 'sci-fi', True),
			('Sport', 'sport', True), ('Thriller', 'thriller', True), ('War', 'war', True), ('Western', 'western', True)]
		for i in genres:
			self.list.append({'name': cleangenre.lang(i[0], self.lang), 'url': self.genre_link % i[1] if i[2] else self.keyword_link % i[1], 'image': 'genres.png', 'icon': 'DefaultGenre.png', 'action': 'movies' })
		self.addDirectory(self.list)
		return self.list

	def languages(self):
		languages = [('Arabic', 'ar'), ('Bosnian', 'bs'), ('Bulgarian', 'bg'), ('Chinese', 'zh'), ('Croatian', 'hr'), ('Dutch', 'nl'),
			('English', 'en'), ('Finnish', 'fi'), ('French', 'fr'), ('German', 'de'), ('Greek', 'el'),('Hebrew', 'he'), ('Hindi ', 'hi'),
			('Hungarian', 'hu'), ('Icelandic', 'is'), ('Italian', 'it'), ('Japanese', 'ja'), ('Korean', 'ko'), ('Macedonian', 'mk'),
			('Norwegian', 'no'), ('Persian', 'fa'), ('Polish', 'pl'), ('Portuguese', 'pt'), ('Punjabi', 'pa'), ('Romanian', 'ro'),
			('Russian', 'ru'), ('Serbian', 'sr'), ('Slovenian', 'sl'), ('Spanish', 'es'), ('Swedish', 'sv'), ('Turkish', 'tr'), ('Ukrainian', 'uk')]
		for i in languages:
			self.list.append({'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'icon': 'DefaultAddonLanguage.png', 'action': 'movies'})
		self.addDirectory(self.list)
		return self.list

	def certifications(self):
		certificates = [
			('General Audience (G)', 'G'),
			('Parental Guidance (PG)', 'PG'),
			('Parental Caution (PG-13)', 'PG-13'),
			('Parental Restriction (R)', 'R'),
			('Mature Audience (NC-17)', 'NC-17')]
		for i in certificates:
			self.list.append({'name': str(i[0]), 'url': self.certification_link % self.certificatesFormat(i[1]), 'image': 'certificates.png', 'icon': 'DefaultMovies.png', 'action': 'movies'})
		self.addDirectory(self.list)
		return self.list

	def certificatesFormat(self, certificates):
		base = 'US%3A'
		if not isinstance(certificates, (tuple, list)):
			certificates = [certificates]
		return ','.join([base + i.upper() for i in certificates])

	def years(self):
		year = (self.date_time.strftime('%Y'))
		for i in range(int(year)-0, 1900, -1):
			self.list.append({'name': str(i), 'url': self.year_link % (str(i), str(i)), 'image': 'years.png', 'icon': 'DefaultYear.png', 'action': 'movies'})
		self.addDirectory(self.list)
		return self.list

	def moviesListToLibrary(self, url):
		url = getattr(self, url + '_link')
		u = urlparse(url).netloc.lower()
		try:
			control.hide()
			if u in self.tmdb_link: items = tmdb_indexer.userlists(url)
			elif u in self.trakt_link: items = self.trakt_user_list(url, self.trakt_user)
			items = [(i['name'], i['url']) for i in items]
			message = 32663
			if 'themoviedb' in url: message = 32681
			select = control.selectDialog([i[0] for i in items], control.lang(message))
			list_name = items[select][0]
			if select == -1: return
			link = items[select][1]
			link = link.split('&sort_by')[0]
			from resources.lib.modules import library
			library.libmovies().range(link, list_name)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			return

	def userlists(self):
		userlists = []
		try:
			if not self.traktCredentials: raise Exception()
			activity = trakt.getActivity()
			self.list = [] ; lists = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
				lists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
			except:
				lists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
			for i in range(len(lists)): lists[i].update({'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
			userlists += lists
		except: pass
		try:
			if not self.traktCredentials: raise Exception()
			self.list = [] ; lists = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
				lists += cache.get(self.trakt_user_list, 3, self.traktlikedlists_link, self.trakt_user)
			except:
				lists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
			for i in range(len(lists)): lists[i].update({'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
			userlists += lists
		except: pass
		try:
			if not self.imdb_user: raise Exception()
			self.list = []
			lists = cache.get(self.imdb_user_list, 0, self.imdblists_link)
			for i in range(len(lists)): lists[i].update({'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
			userlists += lists
		except: pass
		try:
			if self.tmdb_session_id == '': raise Exception()
			self.list = []
			lists = cache.get(tmdb_indexer.userlists, 0, self.tmdb_userlists_link)
			for i in range(len(lists)): lists[i].update({'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbmovies'})
			userlists += lists
		except: pass
		self.list = []
		for i in range(len(userlists)): # Filter the user's own lists that were
			contains = False
			adapted = userlists[i]['url'].replace('/me/', '/%s/' % self.trakt_user)
			for j in range(len(self.list)):
				if adapted == self.list[j]['url'].replace('/me/', '/%s/' % self.trakt_user):
					contains = True
					break
			if not contains: self.list.append(userlists[i])
		if self.tmdb_session_id != '': # TMDb Favorites
			self.list.insert(0, {'name': control.lang(32026), 'url': self.tmdb_favorites_link, 'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbmovies'})
		if self.tmdb_session_id != '': # TMDb Watchlist
			self.list.insert(0, {'name': control.lang(32033), 'url': self.tmdb_watchlist_link, 'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbmovies'})
		if self.imdb_user != '': # imdb Watchlist
			self.list.insert(0, {'name': control.lang(32033), 'url': self.imdbwatchlist_link, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
		if self.imdb_user != '': # imdb My Ratings
			self.list.insert(0, {'name': control.lang(32025), 'url': self.imdbratings_link, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
		if self.traktCredentials: # Trakt Watchlist
			self.list.insert(0, {'name': control.lang(32033), 'url': self.traktwatchlist_link, 'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'movies'})
		self.addDirectory(self.list, queue=True)
		return self.list

	def trakt_list(self, url, user):
		list = []
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			q.update({'extended': 'full'})
			q = (urlencode(q)).replace('%2C', ',')
			u = url.replace('?' + urlparse(url).query, '') + '?' + q
			if '/related' in u: u = u + '&limit=20'
			result = trakt.getTraktAsJson(u)
			if not result: return list
			items = []
			for i in result:
				try:
					movie = i['movie']
					movie['added'] = i.get('listed_at') # for watchlist----confimed it's in response
					movie['paused_at'] = i.get('paused_at', '') # for history
					try: movie['progress'] = max(0, min(1, i['progress'] / 100.0))
					except: movie['progress'] = ''
					try: movie['lastplayed'] = i.get('watched_at', '')
					except: movie['lastplayed'] = ''
					items.append(movie)
				except: pass
			if len(items) == 0: items = result
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			return
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			if int(q['limit']) != len(items): raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse(url).query, '') + '?' + q
		except: next = ''

		def items_list(item):
			try:
				values = item
				values['next'] = next
				values['title'] = item.get('title')
				values['originaltitle'] = values['title']
				try: values['premiered'] = item.get('released', '')[:10]
				except: values['premiered'] = ''
				values['year'] = str(item.get('year', '')) if item.get('year') else ''
				if not values['year']:
					try: values['year'] = str(values['premiered'][:4])
					except: values['year'] = ''
				ids = item.get('ids', {})
				values['imdb'] = str(ids.get('imdb', '')) if ids.get('imdb') else ''
				values['tmdb'] = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
				values['tvdb'] = ''
				# values['studio'] = item.get('network', '') # do not set, some skins show studio icons in place of thumb and looks like dog shit
				values['genre'] = []
				for x in item['genres']: values['genre'].append(x.title())
				if not values['genre']: values['genre'] = 'NA'
				values['duration'] = int(item.get('runtime') * 60) if item.get('runtime') else ''
				values['rating'] = item.get('rating')
				values['votes'] = item['votes']
				values['mpaa'] = item.get('certification', '')
				values['plot'] = item.get('overview')
				values['poster'] = ''
				values['fanart'] = ''
				try: values['trailer'] = control.trailer % item['trailer'].split('v=')[1]
				except: values['trailer'] = ''
				for k in ('released', 'ids', 'genres', 'runtime', 'certification', 'overview', 'comment_count', 'network'): values.pop(k, None) # pop() keys that are not needed anymore
				list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		threads = []
		for item in items: threads.append(workers.Thread(items_list, item))
		[i.start() for i in threads]
		[i.join() for i in threads]
		return list

	def trakt_user_list(self, url, user):
		try:
			result = trakt.getTrakt(url)
			items = jsloads(result)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
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
				from resources.lib.modules import log_utils
				log_utils.error()
		self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return self.list

	def imdb_list(self, url, isRatinglink=False):
		list = []
		try:
			for i in re.findall(r'date\[(\d+)\]', url):
				url = url.replace('date[%s]' % i, (self.date_time - timedelta(days=int(i))).strftime('%Y-%m-%d'))
			def imdb_watchlist_id(url):
				return client.parseDOM(client.request(url), 'meta', ret='content', attrs = {'property': 'pageId'})[0]
			if url == self.imdbwatchlist_link:
				url = cache.get(imdb_watchlist_id, 8640, url)
				url = self.imdbwatchlist2_link % url
			result = client.request(url)
			result = result.replace('\n', ' ')
			items = client.parseDOM(result, 'div', attrs = {'class': '.+? lister-item'}) + client.parseDOM(result, 'div', attrs = {'class': 'lister-item .+?'})
			items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
		except:
			from resources.lib.modules import log_utils
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
				imdb = client.parseDOM(item, 'a', ret='href')[0]
				imdb = re.findall(r'(tt\d*)', imdb)[0]
				try: show = '–'.decode('utf-8') in str(year).decode('utf-8') or '-'.decode('utf-8') in str(year).decode('utf-8') # check with Matrix
				except: show = False
				if show or 'Episode:' in item: raise Exception() # Some lists contain TV shows.
				list.append({'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': '', 'tvdb': '', 'next': next}) # just let super_info() TMDb request provide the meta and pass min to retrieve it
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return list

	def imdb_person_list(self, url):
		self.list = []
		try:
			result = client.request(url)
			items = client.parseDOM(result, 'div', attrs = {'class': '.+?etail'})
		except: return
		for item in items:
			try:
				name = client.parseDOM(item, 'img', ret='alt')[0]
				url = client.parseDOM(item, 'a', ret='href')[0]
				url = re.findall(r'(nm\d*)', url, re.I)[0]
				url = self.person_link % url
				url = client.replaceHTMLCodes(url)
				image = client.parseDOM(item, 'img', ret='src')[0]
				image = re.sub(r'(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
				image = client.replaceHTMLCodes(image)
				self.list.append({'name': name, 'url': url, 'image': image})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return self.list

	def imdb_user_list(self, url):
		list = []
		try:
			result = client.request(url)
			items = client.parseDOM(result, 'li', attrs={'class': 'ipl-zebra-list__item user-list'})
			# items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'}) # breaks the IMDb user list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		for item in items:
			try:
				name = client.parseDOM(item, 'a')[0]
				name = client.replaceHTMLCodes(name)
				url = client.parseDOM(item, 'a', ret='href')[0]
				url = url.split('/list/', 1)[-1].strip('/')
				# url = url.split('/list/', 1)[-1].replace('/', '')
				url = self.imdblist_link % url
				url = client.replaceHTMLCodes(url)
				list.append({'name': name, 'url': url, 'context': url})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		list = sorted(list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return list

	def worker(self, level=1):
		try:
			if not self.list: return
			self.meta = []
			total = len(self.list)
			for i in range(0, total):
				self.list[i].update({'metacache': False})
			self.list = metacache.fetch(self.list, self.lang, self.user)
			for r in range(0, total, 40):
				threads = []
				for i in range(r, r + 40):
					if i < total: threads.append(workers.Thread(self.super_info, i))
				[i.start() for i in threads]
				[i.join() for i in threads]
			if self.meta:
				self.meta = [i for i in self.meta if i.get('tmdb')] # without this "self.list=" below removes missing tmdb but here still writes these cases to metacache?
				metacache.insert(self.meta)
			self.list = [i for i in self.list if i.get('tmdb')]
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def super_info(self, i):
		try:
			if self.list[i]['metacache']: 	return
			imdb = self.list[i].get('imdb', '') ; tmdb = self.list[i].get('tmdb', '')
#### -- Missing id's lookup -- ####
			if not tmdb and imdb:
				try:
					result = tmdb_indexer.Movies().IdLookup(imdb)
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
			if not self.disable_fanarttv:
				extended_art = cache.get(fanarttv.get_movie_art, 168, imdb, tmdb)
				if extended_art: values.update(extended_art)
			values = dict((k, v) for k, v in iter(values.items()) if v is not None and v != '') # remove empty keys so .update() doesn't over-write good meta with empty values.
			self.list[i].update(values)
			meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '', 'lang': self.lang, 'user': self.user, 'item': values}
			self.meta.append(meta)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def movieDirectory(self, items, unfinished=False, next=True):
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32001, message=33049)
		from resources.lib.modules.player import Bookmarks
		sysaddon, syshandle = argv[0], int(argv[1])
		play_mode = control.setting('play.mode')
		is_widget = 'plugin' not in control.infoLabel('Container.PluginName')
		settingFanart = control.setting('fanart') == 'true'
		addonPoster, addonFanart, addonBanner = control.addonPoster(), control.addonFanart(), control.addonBanner()
		indicators = getMovieIndicators(refresh=True)
		if play_mode == '1': playbackMenu = control.lang(32063)
		else: playbackMenu = control.lang(32064)
		if trakt.getTraktIndicatorsInfo():
			watchedMenu, unwatchedMenu = control.lang(32068), control.lang(32069)
		else:
			watchedMenu, unwatchedMenu = control.lang(32066), control.lang(32067)
		playlistManagerMenu, queueMenu = control.lang(35522), control.lang(32065)
		traktManagerMenu, addToLibrary = control.lang(32070), control.lang(32551)
		nextMenu, clearSourcesMenu = control.lang(32053), control.lang(32611)

		for i in items:
			try:
				imdb, tmdb, title, year = i.get('imdb', ''), i.get('tmdb', ''), i['title'], i.get('year', '')
				trailer, runtime = i.get('trailer'), i.get('duration')
				label = '%s (%s)' % (title, year)
				try: labelProgress = label + '[COLOR %s]  [%s][/COLOR]' % (self.highlight_color, str(round(float(i['progress'] * 100), 1)) + '%')
				except: labelProgress = label
				try:
					if int(re.sub(r'[^0-9]', '', str(i['premiered']))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
						labelProgress = '[COLOR %s][I]%s[/I][/COLOR]' % (self.unairedcolor, labelProgress)
				except: pass
				if i.get('traktHistory') is True:
					try:
						air_time = tools.Time.convert(stringTime=i.get('lastplayed', ''), zoneFrom='utc', zoneTo='local', formatInput='%Y-%m-%dT%H:%M:%S.000Z', formatOutput='%b %d %Y %I:%M %p')
						if air_time[12] == '0': air_time = air_time[:12] + '' + air_time[13:]
						labelProgress = labelProgress + '[COLOR %s]  [%s][/COLOR]' % (self.highlight_color, air_time)
					except: pass
				sysname, systitle = quote_plus(label), quote_plus(title)
				meta = dict((k, v) for k, v in iter(i.items()) if v is not None and v != '')
				meta.update({'code': imdb, 'imdbnumber': imdb, 'mediatype': 'movie', 'tag': [imdb, tmdb]})
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass
				poster = meta.get('poster3') or meta.get('poster2') or meta.get('poster') or addonPoster
				fanart = ''
				if settingFanart: fanart = meta.get('fanart3') or meta.get('fanart2') or meta.get('fanart') or addonFanart
				landscape = meta.get('landscape') or fanart
				thumb = meta.get('thumb') or poster or landscape
				icon = meta.get('icon') or poster
				banner = meta.get('banner3') or meta.get('banner2') or meta.get('banner') or addonBanner
				art = {}
				art.update({'icon': icon, 'thumb': thumb, 'banner': banner, 'poster': poster, 'fanart': fanart, 'landscape': landscape, 'clearlogo': meta.get('clearlogo', ''),
								'clearart': meta.get('clearart', ''), 'discart': meta.get('discart', ''), 'keyart': meta.get('keyart', '')})
				for k in ('poster2', 'poster3', 'fanart2', 'fanart3', 'banner2', 'banner3', 'trailer'): meta.pop(k, None)
				meta.update({'poster': poster, 'fanart': fanart, 'banner': banner})
####-Context Menu and Overlays-####
				cm = []
				try:
					overlay = int(getMovieOverlay(indicators, imdb))
					watched = (overlay == 5)
					if self.traktCredentials:
						cm.append((traktManagerMenu, 'RunPlugin(%s?action=tools_traktManager&name=%s&imdb=%s&watched=%s)' % (sysaddon, sysname, imdb, watched)))
					if watched:
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=playcount_Movie&name=%s&imdb=%s&query=4)' % (sysaddon, sysname, imdb)))
						meta.update({'playcount': 1, 'overlay': 5})
						# meta.update({'lastplayed': trakt.watchedMoviesTime(imdb)})
					else:
						cm.append((watchedMenu, 'RunPlugin(%s?action=playcount_Movie&name=%s&imdb=%s&query=5)' % (sysaddon, sysname, imdb)))
						meta.update({'playcount': 0, 'overlay': 4})
				except: pass
				sysmeta, sysart = quote_plus(jsdumps(meta)), quote_plus(jsdumps(art))
				url = '%s?action=play_Item&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, tmdb, sysmeta)
				sysurl = quote_plus(url)
				cm.append((playlistManagerMenu, 'RunPlugin(%s?action=playlist_Manager&name=%s&url=%s&meta=%s&art=%s)' % (sysaddon, sysname, sysurl, sysmeta, sysart)))
				cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem&name=%s)' % (sysaddon, sysname)))
				cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
				cm.append(('Rescrape Item', 'PlayMedia(%s?action=play_Item&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s&rescrape=true)' % (sysaddon, systitle, year, imdb, tmdb, sysmeta)))
				cm.append((addToLibrary, 'RunPlugin(%s?action=library_movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))
				cm.append(('Find similar', 'ActivateWindow(10025,%s?action=movies&url=https://api.trakt.tv/movies/%s/related,return)' % (sysaddon, imdb)))
				cm.append((clearSourcesMenu, 'RunPlugin(%s?action=cache_clearSources)' % sysaddon))
				cm.append(('[COLOR white]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
####################################
				if trailer: meta.update({'trailer': trailer})
				else: meta.update({'trailer': '%s?action=play_Trailer&type=%s&name=%s&year=%s&imdb=%s' % (sysaddon, 'movie', sysname, year, imdb)})
				item = control.item(label=labelProgress, offscreen=True)
				if 'castandart' in i: item.setCast(i['castandart'])
				item.setArt(art)
				item.setUniqueIDs({'imdb': imdb, 'tmdb': tmdb})
				item.setProperty('IsPlayable', 'true')
				if is_widget: item.setProperty('isDG_widget', 'true')
				resumetime = Bookmarks().get(name=label, imdb=imdb, tmdb=tmdb, year=str(year), runtime=runtime, ck=True)
				# item.setProperty('TotalTime', str(meta['duration'])) # Adding this property causes the Kodi bookmark CM items to be added
				item.setProperty('ResumeTime', str(resumetime))
				try:
					watched_percent = round(float(resumetime) / float(runtime) * 100, 1) # resumetime and runtime are both in seconds
					item.setProperty('PercentPlayed', str(watched_percent))
				except: pass
				item.setInfo(type='video', infoLabels=control.metadataClean(meta))
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		if next:
			try:
				if not items: raise Exception()
				url = items[0]['next']
				if not url: raise Exception()
				url_params = dict(parse_qsl(urlsplit(url).query))
				if 'imdb.com' in url and 'start' in url_params:
					page = '  [I](%s)[/I]' % str(int(((int(url_params.get('start')) - 1) / int(self.page_limit)) + 1))
				else:
					page = '  [I](%s)[/I]' % url_params.get('page')
				nextMenu = '[COLOR skyblue]' + nextMenu + page + '[/COLOR]'
				u = urlparse(url).netloc.lower()
				if u not in self.tmdb_link:
					url = '%s?action=moviePage&url=%s' % (sysaddon, quote_plus(url))
				elif u in self.tmdb_link:
					url = '%s?action=tmdbmoviePage&url=%s' % (sysaddon, quote_plus(url))
				item = control.item(label=nextMenu, offscreen=True)
				icon = control.addonNext()
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
				item.setProperty ('SpecialSort', 'bottom')
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		control.content(syshandle, 'movies')
		control.directory(syshandle, cacheToDisc=True)
		control.sleep(500)
		views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})

	def addDirectory(self, items, queue=False):
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32001, message=33049)
		sysaddon, syshandle = argv[0], int(argv[1])
		addonThumb = control.addonThumb()
		artPath = control.artPath()
		queueMenu, playRandom, addToLibrary = control.lang(32065), control.lang(32535), control.lang(32551)
		for i in items:
			try:
				name = i['name']
				if i['image'].startswith('http'): thumb = i['image']
				elif artPath: thumb = control.joinPath(artPath, i['image'])
				else: thumb = addonThumb
				icon = i.get('icon', 0)
				if not icon: icon = 'DefaultFolder.png'
				url = '%s?action=%s' % (sysaddon, i['action'])
				try: url += '&url=%s' % quote_plus(i['url'])
				except: pass
				cm = []
				cm.append((playRandom, 'RunPlugin(%s?action=play_Random&rtype=movie&url=%s)' % (sysaddon, quote_plus(i['url']))))
				if queue: cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem)' % sysaddon))
				try:
					if control.setting('library.service.update') == 'true':
						cm.append((addToLibrary, 'RunPlugin(%s?action=library_moviesToLibrary&url=%s&name=%s)' % (sysaddon, quote_plus(i['context']), name)))
				except: pass
				cm.append(('[COLOR white]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
				item = control.item(label=name, offscreen=True)
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'poster': thumb, 'thumb': thumb, 'fanart': control.addonFanart(), 'banner': thumb})
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		control.content(syshandle, 'addons')
		control.directory(syshandle, cacheToDisc=True)
