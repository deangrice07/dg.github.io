# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from datetime import datetime, timedelta
from json import dumps as jsdumps, loads as jsloads
import re
from threading import Thread
from urllib.parse import quote_plus, urlencode, parse_qsl, urlparse, urlsplit
from resources.lib.database import cache, metacache, fanarttv_cache, traktsync
from resources.lib.indexers import tmdb as tmdb_indexer, fanarttv
from resources.lib.modules import cleangenre
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules.playcount import getTVShowIndicators, getTVShowOverlay, getShowCount
from resources.lib.modules import trakt
from resources.lib.modules import views


class TVshows:
	def __init__(self, notifications=True):
		self.list = []
		self.page_limit = control.setting('page.item.limit')
		self.search_page_limit = control.setting('search.page.limit')
		self.lang = control.apiLanguage()['tmdb']
		self.notifications = notifications
		self.enable_fanarttv = control.setting('enable.fanarttv') == 'true'
		self.prefer_tmdbArt = control.setting('prefer.tmdbArt') == 'true'
		self.highlight_color = control.getHighlightColor()
		self.date_time = datetime.now()
		self.today_date = (self.date_time).strftime('%Y-%m-%d')

		self.tvdb_key = control.setting('tvdb.api.key')
		self.imdb_user = control.setting('imdb.user').replace('ur', '')
		self.user = str(self.imdb_user) + str(self.tvdb_key)

		self.imdb_link = 'https://www.imdb.com'
		self.persons_link = 'https://www.imdb.com/search/name/?count=100&name='
		self.personlist_link = 'https://www.imdb.com/search/name/?count=100&gender=male,female'
		self.popular_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=100,&release_date=,date[0]&sort=moviemeter,asc&count=%s&start=1' % self.page_limit
		self.airing_link = 'https://www.imdb.com/search/title/?title_type=tv_episode&release_date=date[1],date[0]&sort=moviemeter,asc&count=%s&start=1' % self.page_limit
		self.active_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=10,&production_status=active&sort=moviemeter,asc&count=%s&start=1' % self.page_limit
		self.premiere_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&languages=en&num_votes=10,&release_date=date[60],date[0]&sort=release_date,desc&count=%s&start=1' % self.page_limit
		self.rating_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=5000,&release_date=,date[0]&sort=user_rating,desc&count=%s&start=1' % self.page_limit
		self.views_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=100,&release_date=,date[0]&sort=num_votes,desc&count=%s&start=1' % self.page_limit
		self.person_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&release_date=,date[0]&role=%s&sort=year,desc&count=%s&start=1' % ('%s', self.page_limit)
		self.genre_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=3000,&release_date=,date[0]&genres=%s&sort=%s&count=%s&start=1' % ('%s', self.imdb_sort(type='imdbshows'), self.page_limit)
		self.keyword_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&release_date=,date[0]&keywords=%s&sort=%s&count=%s&start=1' % ('%s', self.imdb_sort(type='imdbshows'), self.page_limit)
		self.language_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=100,&production_status=released&primary_language=%s&sort=%s&count=%s&start=1' % ('%s', self.imdb_sort(type='imdbshows'), self.page_limit)
		self.certification_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&release_date=,date[0]&certificates=%s&sort=%s&count=%s&start=1' % ('%s', self.imdb_sort(type='imdbshows'), self.page_limit)
		self.year_link = 'https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=%s&start=1' % ('%s', '%s', self.page_limit)
		self.imdbwatchlist_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user # only used to get users watchlist ID
		self.imdbwatchlist2_link = 'https://www.imdb.com/list/%s/?view=detail&sort=%s&title_type=tvSeries,tvMiniSeries&start=1' % ('%s', self.imdb_sort(type='shows.watchlist'))
		self.imdblists_link = 'https://www.imdb.com/user/ur%s/lists?tab=all&sort=mdfd&order=desc&filter=titles' % self.imdb_user
		self.imdblist_link = 'https://www.imdb.com/list/%s/?view=detail&sort=%s&title_type=tvSeries,tvMiniSeries&start=1' % ('%s', self.imdb_sort())
		self.imdbratings_link = 'https://www.imdb.com/user/ur%s/ratings?sort=your_rating,desc&mode=detail&start=1' % self.imdb_user # IMDb ratings does not take title_type so filter in imdb_list() function
		self.anime_link = 'https://www.imdb.com/search/keyword/?keywords=anime&title_type=tvSeries,miniSeries&release_date=,date[0]&sort=moviemeter,asc&count=%s&start=1' % self.page_limit

		self.trakt_user = control.setting('trakt.username').strip()
		self.traktCredentials = trakt.getTraktCredentialsInfo()
		self.trakt_link = 'https://api.trakt.tv'
		self.search_link = 'https://api.trakt.tv/search/show?limit=%s&page=1&query=' % self.search_page_limit
		self.traktlists_link = 'https://api.trakt.tv/users/me/lists'
		self.traktlikedlists_link = 'https://api.trakt.tv/users/likes/lists?limit=1000000' # used by library import only
		self.traktwatchlist_link = 'https://api.trakt.tv/users/me/watchlist/shows?limit=%s&page=1' % self.page_limit # this is now a dummy link for pagination to work
		self.traktcollection_link = 'https://api.trakt.tv/users/me/collection/shows?limit=%s&page=1' % self.page_limit # this is now a dummy link for pagination to work
		self.traktlist_link = 'https://api.trakt.tv/users/%s/lists/%s/items/shows?limit=%s&page=1' % ('%s', '%s', self.page_limit) # local pagination, limit and page used to advance, pulled from request
		self.progress_link = 'https://api.trakt.tv/sync/watched/shows?extended=noseasons'
		self.trakttrending_link = 'https://api.trakt.tv/shows/trending?page=1&limit=%s' % self.page_limit
		self.traktpopular_link = 'https://api.trakt.tv/shows/popular?page=1&limit=%s' % self.page_limit
		self.traktrecommendations_link = 'https://api.trakt.tv/recommendations/shows?limit=40'
		self.trakt_popularLists_link = 'https://api.trakt.tv/lists/popular?limit=40&page=1' # use limit=40 due to filtering out Movie only lists
		self.trakt_trendingLists_link = 'https://api.trakt.tv/lists/trending?limit=40&page=1'

		self.tvmaze_link = 'https://www.tvmaze.com'
		self.tmdb_key = control.setting('tmdb.api.key')
		if self.tmdb_key == '' or self.tmdb_key is None:
			self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
		self.tmdb_session_id = control.setting('tmdb.session_id')
		self.tmdb_link = 'https://api.themoviedb.org'
		self.tmdb_userlists_link = 'https://api.themoviedb.org/3/account/{account_id}/lists?api_key=%s&language=en-US&session_id=%s&page=1' % ('%s', self.tmdb_session_id) # used by library import only
		self.tmdb_popular_link = 'https://api.themoviedb.org/3/tv/popular?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_toprated_link = 'https://api.themoviedb.org/3/tv/top_rated?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_ontheair_link = 'https://api.themoviedb.org/3/tv/on_the_air?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_airingtoday_link = 'https://api.themoviedb.org/3/tv/airing_today?api_key=%s&language=en-US&region=US&page=1'
		self.tmdb_networks_link = 'https://api.themoviedb.org/3/discover/tv?api_key=%s&with_networks=%s&sort_by=%s&page=1' % ('%s', '%s', self.tmdb_DiscoverSort())
		self.tmdb_genre_link = 'https://api.themoviedb.org/3/discover/tv?api_key=%s&with_genres=%s&include_null_first_air_dates=false&sort_by=%s&page=1' % ('%s', '%s', self.tmdb_DiscoverSort())
		self.tmdb_year_link = 'https://api.themoviedb.org/3/discover/tv?api_key=%s&language=en-US&include_null_first_air_dates=false&first_air_date_year=%s&sort_by=%s&page=1' % ('%s', '%s', self.tmdb_DiscoverSort())
		# Ticket is in to add this feature but currently not available
		# self.tmdb_certification_link = 'https://api.themoviedb.org/3/discover/tv?api_key=%s&language=en-US&certification_country=US&certification=%s&sort_by=%s&page=1' % ('%s', '%s', self.tmdb_DiscoverSort())

	def get(self, url, idx=True, create_directory=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			try: u = urlparse(url).netloc.lower()
			except: pass
			if u in self.trakt_link and '/users/' in url:
				try:
					if '/users/me/' not in url: raise Exception()
					if '/collection/' in url: return self.traktCollection(url)
					if '/watchlist/' in url: return self.traktWatchlist(url)
					if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user):
						self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)
					else: self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
				except:
					self.list = self.trakt_userList(url)
				if idx: self.worker()
				self.sort()
			elif u in self.trakt_link and self.search_link in url:
				self.list = cache.get(self.trakt_list, 6, url, self.trakt_user)
				if idx: self.worker()
			elif u in self.trakt_link:
				self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
				if idx: self.worker()
			elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
				isRatinglink=True if self.imdbratings_link in url else False
				self.list = cache.get(self.imdb_list, 0, url, isRatinglink)
				if idx: self.worker()
				# self.sort() # switched to request sorting for imdb
			elif u in self.imdb_link:
				self.list = cache.get(self.imdb_list, 96, url)
				if idx: self.worker()
			if self.list is None: self.list = []
			if create_directory: self.tvshowDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32002, message=33049)

	def getTMDb(self, url, idx=True, cached=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			try: u = urlparse(url).netloc.lower()
			except: pass
			if u in self.tmdb_link and '/list/' in url:
				self.list = cache.get(tmdb_indexer.TVshows().tmdb_collections_list, 0, url)
			elif u in self.tmdb_link and not '/list/' in url:
				duration = 168 if cached else 0
				self.list = cache.get(tmdb_indexer.TVshows().tmdb_list, duration, url)
			if self.list is None: self.list = []
			if idx: self.tvshowDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32002, message=33049)

	def getTVmaze(self, url, idx=True):
		from resources.lib.indexers import tvmaze
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			self.list = cache.get(tvmaze.tvshows().tvmaze_list, 168, url)
			# if idx: self.worker() ## TVMaze has it's own full list builder.
			if self.list is None: self.list = []
			if idx: self.tvshowDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32002, message=33049)

	def getTraktPublicLists(self, url, create_directory=True):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			if '/popular' in url:
				self.list = cache.get(self.trakt_public_list, 168, url)
			elif '/trending' in url:
				self.list = cache.get(self.trakt_public_list, 48, url)
			else:
				self.list = cache.get(self.trakt_public_list, 24, url)
			if self.list is None: self.list = []
			if create_directory: self.addDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def traktHiddenManager(self, idx=True):
		control.busy()
		try:
			if trakt.getProgressActivity() > cache.timeout(self.trakt_list, self.progress_link, self.trakt_user): raise Exception()
			self.list = cache.get(self.trakt_list, 24, self.progress_link, self.trakt_user)
		except:
			self.list = cache.get(self.trakt_list, 0, self.progress_link, self.trakt_user)
		indicators = getTVShowIndicators(refresh=True)
		for i in self.list:
			count = getShowCount(indicators, imdb=i.get('imdb'), tvdb=i.get('tvdb'))
			i.update({'watched_count': count})
		try:
			hidden = traktsync.fetch_hidden_progress()
			hidden = [str(i['tvdb']) for i in hidden]
			for i in self.list: i.update({'isHidden': 'true'}) if i['tvdb'] in hidden else i.update({'isHidden': ''})
			if idx: self.worker()
			self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=False)
			self.list = sorted(self.list, key=lambda k: k['isHidden'], reverse=True)
			control.hide()
			from resources.lib.windows.trakthidden_manager import TraktHiddenManagerXML
			window = TraktHiddenManagerXML('trakthidden_manager.xml', control.addonPath(control.addonId()), results=self.list)
			chosen_hide, chosen_unhide = window.run()
			del window
			if chosen_unhide:
				success = trakt.unHideItems(chosen_unhide)
				if success: control.notification(title='Trakt Hidden Progress Manager', message='Successfully Unhid %s Item%s' % (len(chosen_unhide), 's' if len(chosen_unhide) >1 else ''))
			if chosen_hide:
				success = trakt.hideItems(chosen_hide)
				if success: control.notification(title='Trakt Hidden Progress Manager', message='Successfully Hid %s Item%s' % (len(chosen_hide), 's' if len(chosen_hide) >1 else ''))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.hide()

	def collectionManager(self):
		try:
			control.busy()
			self.list = traktsync.fetch_collection('shows_collection')
			self.worker()
			self.sort()
			# self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=False)
			control.hide()
			from resources.lib.windows.traktbasic_manager import TraktBasicManagerXML
			window = TraktBasicManagerXML('traktbasic_manager.xml', control.addonPath(control.addonId()), results=self.list)
			selected_items = window.run()
			del window
			if selected_items:
				# refresh = 'plugin.video.dg' in control.infoLabel('Container.PluginName')
				trakt.removeCollectionItems('shows', selected_items)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.hide()

	def watchlistManager(self):
		try:
			control.busy()
			self.list = traktsync.fetch_watch_list('shows_watchlist')
			self.worker()
			self.sort(type='shows.watchlist')
			# self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=False)
			control.hide()
			from resources.lib.windows.traktbasic_manager import TraktBasicManagerXML
			window = TraktBasicManagerXML('traktbasic_manager.xml', control.addonPath(control.addonId()), results=self.list)
			selected_items = window.run()
			del window
			if selected_items:
				# refresh = 'plugin.video.dg' in control.infoLabel('Container.PluginName')
				trakt.removeWatchlistItems('shows', selected_items)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.hide()

	def sort(self, type='shows'):
		try:
			if not self.list: return
			attribute = int(control.setting('sort.%s.type' % type))
			reverse = int(control.setting('sort.%s.order' % type)) == 1
			if attribute == 0: reverse = False # Sorting Order is not enabled when sort method is "Default"
			if attribute > 0:
				if attribute == 1:
					try: self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=reverse)
					except: self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['title'].lower()), reverse=reverse)
				elif attribute == 2: self.list = sorted(self.list, key=lambda k: float(k['rating']), reverse=reverse)
				elif attribute == 3: self.list = sorted(self.list, key=lambda k: int(str(k['votes']).replace(',', '')), reverse=reverse)
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

	def imdb_sort(self, type='shows'):
		sort = int(control.setting('sort.%s.type' % type))
		imdb_sort = 'list_order' if type == 'shows.watchlist' else 'moviemeter'
		if sort == 1: imdb_sort = 'alpha'
		if sort == 2: imdb_sort = 'user_rating'
		if sort == 3: imdb_sort = 'num_votes'
		if sort == 4: imdb_sort = 'release_date'
		if sort in (5, 6): imdb_sort = 'date_added'
		imdb_sort_order = ',asc' if (int(control.setting('sort.%s.order' % type)) == 0 or sort == 0) else ',desc'
		sort_string = imdb_sort + imdb_sort_order
		return sort_string

	def tmdb_DiscoverSort(self):
		sort = int(control.setting('sort.shows.type'))
		tmdb_sort = 'popularity' # default sort=0
		# if sort == 1: tmdb_sort = 'original_title'
		if sort == 1: tmdb_sort = 'title'
		if sort == 2: tmdb_sort = 'vote_average'
		if sort == 3: tmdb_sort = 'vote_count'
		if sort in (4, 5, 6): tmdb_sort = 'primary_release_date'
		tmdb_sort_order = '.asc' if (int(control.setting('sort.movies.order')) == 0) else '.desc'
		sort_string = tmdb_sort + tmdb_sort_order
		if sort == 2: sort_string = sort_string + '&vote_count.gte=500'
		return sort_string

	def search(self):
		from resources.lib.menus import navigator
		navigator.Navigator().addDirectoryItem(32603, 'tvSearchnew', 'search.png', 'DefaultAddonsSearch.png', isFolder=False)
		try: from sqlite3 import dbapi2 as database
		except ImportError: from pysqlite2 import dbapi2 as database
		try:
			if not control.existsPath(control.dataPath): control.makeFile(control.dataPath)
			dbcon = database.connect(control.searchFile)
			dbcur = dbcon.cursor()
			dbcur.executescript('''CREATE TABLE IF NOT EXISTS tvshow (ID Integer PRIMARY KEY AUTOINCREMENT, term);''')
			dbcur.execute('''SELECT * FROM tvshow ORDER BY ID DESC''')
			dbcur.connection.commit()
			lst = []
			delete_option = False
			for (id, term) in dbcur.fetchall():
				if term not in str(lst):
					delete_option = True
					navigator.Navigator().addDirectoryItem(term, 'tvSearchterm&name=%s' % term, 'search.png', 'DefaultAddonsSearch.png', isSearch=True, table='tvshow')
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
		if not q: return control.closeAll()
		try: from sqlite3 import dbapi2 as database
		except ImportError: from pysqlite2 import dbapi2 as database
		try:
			dbcon = database.connect(control.searchFile)
			dbcur = dbcon.cursor()
			dbcur.execute('''INSERT INTO tvshow VALUES (?,?)''', (None, q))
			dbcur.connection.commit()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()
		url = self.search_link + quote_plus(q)
		control.closeAll()
		control.execute('ActivateWindow(Videos,plugin://plugin.video.dg/?action=tvshows&url=%s,return)' % (quote_plus(url)))

	def search_term(self, name):
		url = self.search_link + quote_plus(name)
		self.get(url)

	def person(self):
		k = control.keyboard('', control.lang(32010))
		k.doModal()
		q = k.getText().strip() if k.isConfirmed() else None
		if not q: return control.closeAll()
		url = self.persons_link + quote_plus(q)
		control.closeAll()
		control.execute('ActivateWindow(Videos,plugin://plugin.video.dg/?action=tvPersons&url=%s,return)' % (quote_plus(url)))

	def persons(self, url):
		if url is None: self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
		else: self.list = cache.get(self.imdb_person_list, 1, url)
		if self.list is None: self.list = []
		if self.list:
			for i in range(0, len(self.list)): self.list[i].update({'content': 'actors', 'icon': 'DefaultActor.png', 'action': 'tvshows'})
		self.addDirectory(self.list)
		return self.list

	def genres(self, url):
		try: url = getattr(self, url + '_link')
		except: pass
		genres = [
			('Action', 'action', True, '10759'), ('Adventure', 'adventure', True), ('Animation', 'animation', True, '16'), ('Anime', 'anime', False),
			('Biography', 'biography', True), ('Comedy', 'comedy', True, '35'), ('Crime', 'crime', True, '80'), ('Drama', 'drama', True, '18'),
			('Family', 'family', True, '10751'), ('Fantasy', 'fantasy', True), ('Game-Show', 'game_show', True), ('History', 'history', True),
			('Horror', 'horror', True), ('Music', 'music', True), ('Musical', 'musical', True), ('Mystery', 'mystery', True, '9648'),
			('News', 'news', True, '10763'), ('Reality', 'reality_tv', True, '10764'), ('Romance', 'romance', True), ('Science Fiction', 'sci_fi', True, '10765'),
			('Sport', 'sport', True), ('Talk-Show', 'talk_show', True, '10767'), ('Thriller', 'thriller', True), ('War', 'war', True, '10768'), ('Western', 'western', True, '37')]
		for i in genres:
			if self.imdb_link in url: self.list.append({'content': 'genres', 'name': cleangenre.lang(i[0], self.lang), 'url': url % i[1] if i[2] else self.keyword_link % i[1], 'image': i[0] + '.jpg', 'icon': i[0] + '.png', 'action': 'tvshows'})
			if self.tmdb_link in url:
				try: self.list.append({'content': 'genres', 'name': cleangenre.lang(i[0], self.lang), 'url': url % ('%s', i[3]), 'image': i[0] + '.jpg', 'icon': i[0] + '.png', 'action': 'tmdbTvshows'})
				except: pass
		self.addDirectory(self.list)
		return self.list

	def networks(self):
		networks = tmdb_indexer.TVshows().get_networks()
		for i in networks:
			self.list.append({'content': 'studios', 'name': i[0], 'url': self.tmdb_networks_link % ('%s', i[1]), 'image': i[2], 'icon': i[2], 'action': 'tmdbTvshows'})
		self.addDirectory(self.list)
		return self.list

	def originals(self):
		originals = tmdb_indexer.TVshows().get_originals()
		for i in originals:
			self.list.append({'content': 'studios', 'name': i[0], 'url': self.tmdb_networks_link % ('%s', i[1]), 'image': i[2], 'icon': i[2], 'action': 'tmdbTvshows'})
		self.addDirectory(self.list)
		return self.list

	def languages(self):
		languages = [
			('Arabic', 'ar'), ('Bosnian', 'bs'), ('Bulgarian', 'bg'), ('Chinese', 'zh'), ('Croatian', 'hr'), ('Dutch', 'nl'), ('English', 'en'), ('Finnish', 'fi'),
			('French', 'fr'), ('German', 'de'), ('Greek', 'el'), ('Hebrew', 'he'), ('Hindi ', 'hi'), ('Hungarian', 'hu'), ('Icelandic', 'is'), ('Italian', 'it'),
			('Japanese', 'ja'), ('Korean', 'ko'), ('Norwegian', 'no'), ('Persian', 'fa'), ('Polish', 'pl'), ('Portuguese', 'pt'), ('Punjabi', 'pa'),
			('Romanian', 'ro'), ('Russian', 'ru'), ('Serbian', 'sr'), ('Spanish', 'es'), ('Swedish', 'sv'), ('Turkish', 'tr'), ('Ukrainian', 'uk')]
		for i in languages:
			self.list.append({'content': 'countries', 'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'icon': 'DefaultAddonLanguage.png', 'action': 'tvshows'})
		self.addDirectory(self.list)
		return self.list

	def certifications(self):
		certificates = [
			('Child Audience (TV-Y)', 'US%3ATV-Y'),
			('Young Audience (TV-Y7)', 'US%3ATV-Y7'),
			('General Audience (TV-G)', 'US%3ATV-G'),
			('Parental Guidance (TV-PG)', 'US%3ATV-PG'),
			('Youth Audience (TV-14)', 'US%3ATV-14'),
			('Mature Audience (TV-MA)', 'US%3ATV-MA')]
		for i in certificates:
			self.list.append({'content': 'tags', 'name': str(i[0]), 'url': self.certification_link % i[1], 'image': 'certificates.png', 'icon': 'certificates.png', 'action': 'tvshows'})
		self.addDirectory(self.list)
		return self.list

	def years(self, url):
		try: url = getattr(self, url + '_link')
		except: pass
		year = (self.date_time.strftime('%Y'))
		for i in range(int(year)-0, 1900, -1):
			if self.imdb_link in url: self.list.append({'content': 'years', 'name': str(i), 'url': url % (str(i), str(i)), 'image': 'years.png', 'icon': 'DefaultYear.png', 'action': 'tvshows'})
			if self.tmdb_link in url: self.list.append({'content': 'years', 'name': str(i), 'url': url % ('%s', str(i)), 'image': 'years.png', 'icon': 'DefaultYear.png', 'action': 'tmdbTvshows'})
		self.addDirectory(self.list)
		return self.list

	def tvshowsListToLibrary(self, url):
		url = getattr(self, url + '_link')
		u = urlparse(url).netloc.lower()
		try:
			control.hide()
			if u in self.tmdb_link: items = tmdb_indexer.userlists(url)
			elif u in self.trakt_link:
				if url in self.traktlikedlists_link:
					items = self.traktLlikedlists()
				else: items = self.trakt_user_lists(url, self.trakt_user)
			items = [(i['name'], i['url']) for i in items]
			message = 32663
			if 'themoviedb' in url: message = 32681
			select = control.selectDialog([i[0] for i in items], control.lang(message))
			list_name = items[select][0]
			if select == -1: return
			link = items[select][1]
			link = link.split('&sort_by')[0]
			link = link.split('?limit=')[0]
			from resources.lib.modules import library
			library.libtvshows().range(link, list_name)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def userlists(self):
		userlists = []
		try:
			if not self.traktCredentials: raise Exception()
			activity = trakt.getActivity()
			self.list = [] ; lists = []
			try:
				if activity > cache.timeout(self.trakt_user_lists, self.traktlists_link, self.trakt_user): raise Exception()
				lists += cache.get(self.trakt_user_lists, 720, self.traktlists_link, self.trakt_user)
			except:
				lists += cache.get(self.trakt_user_lists, 0, self.traktlists_link, self.trakt_user)
			userlists += lists
		except: pass
		try:
			if not self.imdb_user: raise Exception()
			self.list = []
			lists = cache.get(self.imdb_user_list, 0, self.imdblists_link)
			userlists += lists
		except: pass
		try:
			if self.tmdb_session_id == '': raise Exception()
			self.list = []
			url = self.tmdb_link + '/3/account/{account_id}/lists?api_key=%s&language=en-US&session_id=%s&page=1' % ('%s', self.tmdb_session_id)
			lists = cache.get(tmdb_indexer.userlists, 0, url)
			for i in range(len(lists)): lists[i].update({'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbTvshows'})
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
			url = self.tmdb_link + '/3/account/{account_id}/favorite/tv?api_key=%s&session_id=%s&sort_by=created_at.asc&page=1' % ('%s', self.tmdb_session_id)
			self.list.insert(0, {'name': control.lang(32026), 'url': url, 'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbTvshows'})
		if self.tmdb_session_id != '': # TMDb Watchlist
			url = self.tmdb_link + '/3/account/{account_id}/watchlist/tv?api_key=%s&session_id=%s&sort_by=created_at.asc&page=1' % ('%s', self.tmdb_session_id)
			self.list.insert(0, {'name': control.lang(32033), 'url': url, 'image': 'tmdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tmdbTvshows'})
		if self.imdb_user != '': # imdb Watchlist
			self.list.insert(0, {'name': control.lang(32033), 'url': self.imdbwatchlist_link, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
		if self.imdb_user != '': # imdb My Ratings
			self.list.insert(0, {'name': control.lang(32025), 'url': self.imdbratings_link, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
		self.addDirectory(self.list)
		return self.list

	def traktCollection(self, url, create_directory=True):
		self.list = []
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			index = int(q['page']) - 1
			self.list = traktsync.fetch_collection('shows_collection')
			self.sort() # sort before local pagination
			if control.setting('trakt.paginate.lists') == 'true' and self.list:
				paginated_ids = [self.list[x:x + int(self.page_limit)] for x in range(0, len(self.list), int(self.page_limit))]
				self.list = paginated_ids[index]
			try:
				if int(q['limit']) != len(self.list): raise Exception()
				q.update({'page': str(int(q['page']) + 1)})
				q = (urlencode(q)).replace('%2C', ',')
				next = url.replace('?' + urlparse(url).query, '') + '?' + q
			except: next = ''
			for i in range(len(self.list)): self.list[i]['next'] = next
			self.worker()
			if self.list is None: self.list = []
			if create_directory: self.tvshowDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def traktWatchlist(self, url, create_directory=True):
		self.list = []
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			index = int(q['page']) - 1
			self.list = traktsync.fetch_watch_list('shows_watchlist')
			self.sort(type='shows.watchlist') # sort before local pagination
			if control.setting('trakt.paginate.lists') == 'true' and self.list:
				paginated_ids = [self.list[x:x + int(self.page_limit)] for x in range(0, len(self.list), int(self.page_limit))]
				self.list = paginated_ids[index]
			try:
				if int(q['limit']) != len(self.list): raise Exception()
				q.update({'page': str(int(q['page']) + 1)})
				q = (urlencode(q)).replace('%2C', ',')
				next = url.replace('?' + urlparse(url).query, '') + '?' + q
			except: next = ''
			for i in range(len(self.list)): self.list[i]['next'] = next
			self.worker()
			if self.list is None: self.list = []
			if create_directory: self.tvshowDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def traktLlikedlists(self):
		items = traktsync.fetch_liked_list('', True)
		for item in items:
			try:
				if item['content_type'] == 'movies': continue
				list_name = item['list_name']
				list_owner = item['list_owner']
				list_owner_slug = item['list_owner_slug']
				list_id = item['trakt_id']
				list_url = self.traktlist_link % (list_owner_slug, list_id)
				next = ''
				label = '%s - [COLOR %s]%s[/COLOR]' % (list_name, self.highlight_color, list_owner)
				self.list.append({'name': label, 'list_type': 'traktPulicList', 'url': list_url, 'list_owner': list_owner, 'list_name': list_name, 'list_id': list_id, 'context': list_url, 'next': next, 'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		self.addDirectory(self.list, queue=True)
		return self.list

	def trakt_list(self, url, user):
		self.list = []
		if '/related' in url: url = url + '?limit=20'
		items = trakt.getTraktAsJson(url)
		if not items: return
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			if int(q['limit']) != len(items): raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse(url).query, '') + '?' + q
		except: next = ''
		for item in items: # rating and votes via TMDb, or I must use `extended=full and it slows down
			try:
				values = {}
				values['next'] = next 
				values['added'] = item.get('listed_at', '')
				values['paused_at'] = item.get('paused_at', '') # for unfinished
				try: values['progress'] = item['progress']
				except: values['progress'] = None
				values['lastplayed'] = item.get('watched_at', '') # for history
				show = item.get('show') or item
				values['title'] = show.get('title')
				values['originaltitle'] = values['title']
				values['tvshowtitle'] = values['title']
				values['year'] = str(show.get('year')) if show.get('year') else ''
				ids = show.get('ids', {})
				values['imdb'] = str(ids.get('imdb', '')) if ids.get('imdb', '') else ''
				values['tmdb'] = str(ids.get('tmdb')) if ids.get('tmdb', '') else ''
				values['tvdb'] = str(ids.get('tvdb')) if ids.get('tvdb', '') else ''
				self.list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return self.list

	def trakt_userList(self, url, create_directory=True):
		self.list = []
		q = dict(parse_qsl(urlsplit(url).query))
		index = int(q['page']) - 1
		def userList_totalItems(url):
			items = trakt.getTraktAsJson(url)
			if not items: return
			for item in items:
				try:
					values = {}
					values['added'] = item.get('listed_at', '')
					show = item['show']
					values['title'] = show.get('title')
					values['originaltitle'] = values['title']
					values['tvshowtitle'] = values['title']
					try: values['premiered'] = show.get('first_aired', '')[:10]
					except: values['premiered'] = ''
					values['year'] = str(show.get('year', '')) if show.get('year') else ''
					if not values['year']:
						try: values['year'] = str(values['premiered'][:4])
						except: values['year'] = ''
					ids = show.get('ids', {})
					values['imdb'] = str(ids.get('imdb', '')) if ids.get('imdb') else ''
					values['tmdb'] = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
					values['tvdb'] = str(ids.get('tvdb')) if ids.get('tvdb', '') else ''
					values['rating'] = show.get('rating')
					values['votes'] = show.get('votes')
					airs = show.get('airs', {})
					values['airday'] = airs['day']
					values['airtime'] = airs['time']
					values['airzone'] = airs['timezone']
					self.list.append(values)
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
			return self.list
		self.list = cache.get(userList_totalItems, 48, url.split('limit')[0] + 'extended=full')
		if not self.list: return
		self.sort() # sort before local pagination
		total_pages = 1
		if control.setting('trakt.paginate.lists') == 'true':
			paginated_ids = [self.list[x:x + int(self.page_limit)] for x in range(0, len(self.list), int(self.page_limit))]
			total_pages = len(paginated_ids)
			self.list = paginated_ids[index]
		try:
			if int(q['limit']) != len(self.list): raise Exception()
			if int(q['page']) == total_pages: raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse(url).query, '') + '?' + q
		except: next = ''
		for i in range(len(self.list)): self.list[i]['next'] = next
		self.worker()
		if self.list is None: self.list = []
		if create_directory: self.tvshowDirectory(self.list)
		return self.list

	def trakt_user_lists(self, url, user):
		items = traktsync.fetch_user_lists('', True)
		for item in items:
			try:
				if item['content_type'] == 'movies': continue
				list_name = item['list_name']
				list_owner = item['list_owner']
				list_owner_slug = item['list_owner_slug']
				list_id = item['trakt_id']
				list_url = self.traktlist_link % (list_owner_slug, list_id)
				next = ''
				label = '%s - [COLOR %s]%s[/COLOR]' % (list_name, self.highlight_color, list_owner)
				self.list.append({'name': label, 'url': list_url, 'list_owner': list_owner, 'list_name': list_name, 'list_id': list_id, 'context': list_url, 'next': next, 'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return self.list

	def trakt_public_list(self, url):
		try:
			result = trakt.getTrakt(url)
			items = jsloads(result)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			if int(q['limit']) != len(items): raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse(url).query, '') + '?' + q
		except: next = ''

		for item in items:
			try:
				if item.get('type', '') == 'officiallist': continue #seems bugy so until Justin replies hold off
				list_item = item.get('list', {})
				list_name = list_item.get('name', '')
				list_id = list_item.get('ids', {}).get('trakt', '')
				list_owner = list_item.get('user', {}).get('username', '')
				list_owner_slug = list_item.get('user', {}).get('ids', {}).get('slug', '')
				if any(list_item.get('privacy', '') == value for value in ('private', 'friends')): continue
				list_url = self.traktlist_link % (list_owner_slug, list_id)
				list_content = traktsync.fetch_public_list(list_id)
				if not list_content: pass
				else: 
					if list_content.get('content_type', '') == 'movies': continue
				label = '%s - [COLOR %s]%s[/COLOR]' % (list_name, self.highlight_color, list_owner)
				self.list.append({'name': label, 'list_type': 'traktPulicList', 'url': list_url, 'list_owner': list_owner, 'list_name': list_name, 'list_id': list_id, 'context': list_url, 'next': next, 'image': 'trakt.png', 'icon': 'trakt.png', 'action': 'tvshows'})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return self.list

	def imdb_list(self, url, isRatinglink=False):
		list = [] ; items = [] ; dupes = []
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
		try:
			# HTML syntax error, " directly followed by attribute name. Insert space in between. parseDOM can otherwise not handle it.
			result = result.replace('"class="lister-page-next', '" class="lister-page-next')
			next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})
			if len(next) == 0:
				next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
				next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
				next = [i[0] for i in next if 'Next' in i[1]]
			next = url.replace(urlparse(url).query, urlparse(next[0]).query)
			next = client.replaceHTMLCodes(next)
		except:
			next = ''
		for item in items:
			try:
				title = client.replaceHTMLCodes(client.parseDOM(item, 'a')[1])
				year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
				year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
				year = re.findall(r'(\d{4})', year[0])[0]
				if int(year) > int((self.date_time).strftime('%Y')): raise Exception()
				imdb = client.parseDOM(item, 'a', ret='href')[0]
				imdb = re.findall(r'(tt\d*)', imdb)[0]
				if imdb in dupes: raise Exception()
				dupes.append(imdb)
				rating = votes = ''
				try:
					rating = client.parseDOM(item, 'div', attrs = {'class': 'ratings-bar'})
					rating = client.parseDOM(rating, 'strong')[0]
				except:
					try:
						rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})
						rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
					except:
						try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0] 
						except:
							try: rating = client.parseDOM(item, 'span', attrs = {'class': 'ipl-rating-star__rating'})[0]
							except: rating = ''
				try: votes = client.parseDOM(item, 'span', attrs = {'name': 'nv'})[0]
				except:
					try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
					except:
						try: votes = re.findall(r'\((.+?) vote(?:s|)\)', votes)[0]
						except: votes = ''
				list.append({'title': title, 'tvshowtitle': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': '', 'tvdb': '', 'rating': rating, 'votes': votes, 'next': next})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return list

	def imdb_person_list(self, url):
		list = []
		try:
			result = client.request(url)
			items = client.parseDOM(result, 'div', attrs = {'class': '.+? mode-detail'})
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
				list.append({'name': name, 'url': url, 'image': image})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return list

	def imdb_user_list(self, url):
		list = []
		try:
			result = client.request(url)
			items = client.parseDOM(result, 'li', attrs={'class': 'ipl-zebra-list__item user-list'})
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		for item in items:
			try:
				name = client.parseDOM(item, 'a')[0]
				name = client.replaceHTMLCodes(name)
				url = client.parseDOM(item, 'a', ret='href')[0]
				url = url.split('/list/', 1)[-1].strip('/')
				url = self.imdblist_link % url
				url = client.replaceHTMLCodes(url)
				list.append({'name': name, 'url': url, 'context': url, 'image': 'imdb.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		list = sorted(list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return list

	def worker(self):
		try:
			if not self.list: return
			self.meta = []
			total = len(self.list)
			for i in range(0, total): self.list[i].update({'metacache': False})
			self.list = metacache.fetch(self.list, self.lang, self.user)
			for r in range(0, total, 40):
				threads = []
				for i in range(r, r + 40):
					if i < total: threads.append(Thread(target=self.super_info, args=(i,)))
				[i.start() for i in threads]
				[i.join() for i in threads]
			if self.meta:
				self.meta = [i for i in self.meta if i.get('tmdb')] # without this "self.list=" below removes missing tmdb but here still writes these cases to metacache?
				metacache.insert(self.meta)
			self.list = [i for i in self.list if i.get('tmdb')] # to rid missing tmdb_id's because season list can not load without
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def super_info(self, i):
		try:
			if self.list[i]['metacache']: return
			imdb = self.list[i].get('imdb', '') ; tmdb = self.list[i].get('tmdb', '') ; tvdb = self.list[i].get('tvdb', '')
#### -- Missing id's lookup -- ####
			trakt_ids = None
			if (not tmdb or not tvdb) and imdb: trakt_ids = trakt.IdLookup('imdb', imdb, 'show')
			elif (not tmdb or not imdb) and tvdb: trakt_ids = trakt.IdLookup('tvdb', tvdb, 'show')
			if trakt_ids:
				if not imdb: imdb = str(trakt_ids.get('imdb', '')) if trakt_ids.get('imdb') else ''
				if not tmdb: tmdb = str(trakt_ids.get('tmdb', '')) if trakt_ids.get('tmdb') else ''
				if not tvdb: tvdb = str(trakt_ids.get('tvdb', '')) if trakt_ids.get('tvdb') else ''
			if not tmdb and (imdb or tvdb):
				try:
					result = cache.get(tmdb_indexer.TVshows().IdLookup, 96, imdb, tvdb)
					tmdb = str(result.get('id', '')) if result.get('id') else ''
				except: tmdb = ''
			if not imdb or not tmdb or not tvdb:
				try:
					results = trakt.SearchTVShow(quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)
					if results[0]['show']['title'].lower() != self.list[i]['title'].lower() or int(results[0]['show']['year']) != int(self.list[i]['year']): return # Trakt has "THEM" and "Them" twice for same show, use .lower()
					ids = results[0].get('show', {}).get('ids', {})
					if not imdb: imdb = str(ids.get('imdb', '')) if ids.get('imdb') else ''
					if not tmdb: tmdb = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
					if not tvdb: tvdb = str(ids.get('tvdb', '')) if ids.get('tvdb') else ''
				except: pass
#################################
			if not tmdb:
				if control.setting('debug.level') != '1': return
				from resources.lib.modules import log_utils
				return log_utils.log('tvshowtitle: (%s) missing tmdb_id: ids={imdb: %s, tmdb: %s, tvdb: %s}' % (self.list[i]['title'], imdb, tmdb, tvdb), __name__, log_utils.LOGDEBUG) # log TMDb shows that they do not have
			showSeasons = cache.get(tmdb_indexer.TVshows().get_showSeasons_meta, 96, tmdb)
			if not showSeasons: return
			values = {}
			values.update(showSeasons)
			if 'rating' in self.list[i] and self.list[i]['rating']: values['rating'] = self.list[i]['rating'] # prefer imdb,trakt rating and votes if set
			if 'votes' in self.list[i] and self.list[i]['votes']: values['votes'] = self.list[i]['votes']
			if 'year' in self.list[i] and self.list[i]['year'] != values.get('year'): values['year'] = self.list[i]['year']
			if not tvdb: tvdb = values.get('tvdb', '')
			if not values.get('imdb'): values['imdb'] = imdb
			if not values.get('tmdb'): values['tmdb'] = tmdb
			if not values.get('tvdb'): values['tvdb'] = tvdb
			if self.lang != 'en':
				try:
					if 'available_translations' in self.list[i] and self.lang not in self.list[i]['available_translations']: raise Exception()
					trans_item = trakt.getTVShowTranslation(imdb, lang=self.lang, full=True)
					if trans_item:
						if trans_item.get('title'):
							values['tvshowtitle'] = trans_item.get('title')
							values['title'] = trans_item.get('title')
						if trans_item.get('overview'): values['plot'] =trans_item.get('overview')
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
			if self.enable_fanarttv:
				extended_art = fanarttv_cache.get(fanarttv.get_tvshow_art, 168, tvdb)
				if extended_art: values.update(extended_art)
			values = dict((k, v) for k, v in iter(values.items()) if v is not None and v != '') # remove empty keys so .update() doesn't over-write good meta with empty values.
			self.list[i].update(values)
			meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': values}
			self.meta.append(meta)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def tvshowDirectory(self, items, next=True):
		from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
		control.playlist.clear()
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32002, message=33049)
		sysaddon, syshandle = argv[0], int(argv[1])
		is_widget = 'plugin' not in control.infoLabel('Container.PluginName')
		settingFanart = control.setting('fanart') == 'true'
		addonPoster, addonFanart, addonBanner = control.addonPoster(), control.addonFanart(), control.addonBanner()
		indicators = getTVShowIndicators(refresh=True)
		unwatchedEnabled = control.setting('tvshows.unwatched.enabled') == 'true'
		flatten = control.setting('flatten.tvshows') == 'true'
		if trakt.getTraktIndicatorsInfo():
			watchedMenu, unwatchedMenu = control.lang(32068), control.lang(32069)
		else:
			watchedMenu, unwatchedMenu = control.lang(32066), control.lang(32067)
		traktManagerMenu, queueMenu = control.lang(32070), control.lang(32065)
		showPlaylistMenu, clearPlaylistMenu = control.lang(35517), control.lang(35516)
		playRandom, addToLibrary = control.lang(32535), control.lang(32551)
		nextMenu, findSimilarMenu = control.lang(32053), control.lang(32184)

		for i in items:
			try:
				imdb, tmdb, tvdb, year, trailer = i.get('imdb', ''), i.get('tmdb', ''), i.get('tvdb', ''), i.get('year', ''), i.get('trailer', '')
				title = i.get('tvshowtitle') or i.get('title')
				systitle = quote_plus(title)
				meta = dict((k, v) for k, v in iter(i.items()) if v is not None and v != '')
				meta.update({'code': imdb, 'imdbnumber': imdb, 'mediatype': 'tvshow', 'tag': [imdb, tmdb]}) # "tag" and "tagline" for movies only, but works in my skin mod so leave
				if unwatchedEnabled: trakt.seasonCount(imdb) # pre-cache season counts for the listed shows
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass
				try:
					if 'tvshowtitle' not in meta: meta.update({'tvshowtitle': title})
				except: pass
				if self.prefer_tmdbArt: poster = meta.get('poster3') or meta.get('poster') or meta.get('poster2') or addonPoster
				else: poster = meta.get('poster2') or meta.get('poster3') or meta.get('poster') or addonPoster
				landscape = meta.get('landscape')
				fanart = ''
				if settingFanart:
					if self.prefer_tmdbArt: fanart = meta.get('fanart3') or meta.get('fanart') or meta.get('fanart2') or addonFanart
					else: fanart = meta.get('fanart2') or meta.get('fanart3') or meta.get('fanart') or addonFanart
				thumb = meta.get('thumb') or poster or landscape # set to show level poster
				icon = meta.get('icon') or poster
				banner = meta.get('banner3') or meta.get('banner2') or meta.get('banner') or addonBanner
				art = {}
				art.update({'poster': poster, 'tvshow.poster': poster, 'fanart': fanart, 'icon': icon, 'thumb': thumb, 'banner': banner, 'clearlogo': meta.get('clearlogo', ''),
						'tvshow.clearlogo': meta.get('clearlogo', ''), 'clearart': meta.get('clearart', ''), 'tvshow.clearart': meta.get('clearart', ''), 'landscape': landscape})
				for k in ('poster2', 'poster3', 'fanart2', 'fanart3', 'banner2', 'banner3', 'trailer'): meta.pop(k, None)
				meta.update({'poster': poster, 'fanart': fanart, 'banner': banner, 'thumb': thumb, 'icon': icon})
####-Context Menu and Overlays-####
				cm = []
				try:
					overlay = int(getTVShowOverlay(indicators, imdb, tvdb))
					watched = (overlay == 5)
					if self.traktCredentials:
						cm.append((traktManagerMenu, 'RunPlugin(%s?action=tools_traktManager&name=%s&imdb=%s&tvdb=%s&watched=%s)' % (sysaddon, systitle, imdb, tvdb, watched)))
					if watched:
						meta.update({'playcount': 1, 'overlay': 5})
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=playcount_TVShow&name=%s&imdb=%s&tvdb=%s&query=4)' % (sysaddon, systitle, imdb, tvdb)))
					else:
						meta.update({'playcount': 0, 'overlay': 4})
						cm.append((watchedMenu, 'RunPlugin(%s?action=playcount_TVShow&name=%s&imdb=%s&tvdb=%s&query=5)' % (sysaddon, systitle, imdb, tvdb)))
				except: pass
				sysmeta, sysart = quote_plus(jsdumps(meta)), quote_plus(jsdumps(art))
				cm.append((findSimilarMenu, 'ActivateWindow(10025,%s?action=tvshows&url=https://api.trakt.tv/shows/%s/related,return)' % (sysaddon, imdb)))
				cm.append((playRandom, 'RunPlugin(%s?action=play_Random&rtype=season&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&art=%s)' % (sysaddon, systitle, year, imdb, tmdb, tvdb, sysart)))
				cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem&name=%s)' % (sysaddon, systitle)))
				cm.append((showPlaylistMenu, 'RunPlugin(%s?action=playlist_Show)' % sysaddon))
				cm.append((clearPlaylistMenu, 'RunPlugin(%s?action=playlist_Clear)' % sysaddon))
				cm.append((addToLibrary, 'RunPlugin(%s?action=library_tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s)' % (sysaddon, systitle, year, imdb, tmdb, tvdb)))
				cm.append(('[COLOR ghostwhite]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
####################################
				if flatten: url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, sysmeta)
				else: url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&art=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, sysart)
				if trailer: meta.update({'trailer': trailer}) # removed temp so it's not passed to CM items, only skin
				else: meta.update({'trailer': '%s?action=play_Trailer&type=%s&name=%s&year=%s&imdb=%s' % (sysaddon, 'show', systitle, year, imdb)})
				item = control.item(label=title, offscreen=True)
				if 'castandart' in i: item.setCast(i['castandart'])
				item.setArt(art)
				if unwatchedEnabled:
					try: 
						count = getShowCount(indicators, imdb, tvdb) # this is threaded without .join() so not all results are immediately seen
						if count:
							item.setProperties({'WatchedEpisodes': str(count['watched']), 'UnWatchedEpisodes': str(count['unwatched'])})
							item.setProperties({'TotalSeasons': str(meta.get('total_seasons', '')), 'TotalEpisodes': str(count['total'])})
						else:
							item.setProperties({'WatchedEpisodes': '0', 'UnWatchedEpisodes': str(meta.get('total_aired_episodes', ''))}) # temp use TMDb's "total_aired_episodes" for threads not finished....next load counts will update with trakt data
							item.setProperties({'TotalSeasons': str(meta.get('total_seasons', '')), 'TotalEpisodes': str(meta.get('total_aired_episodes', ''))})
					except: pass
				item.setProperty('IsPlayable', 'false')
				item.setProperty('tmdb_id', str(tmdb))
				if is_widget: item.setProperty('isDG_widget', 'true')
				item.setUniqueIDs({'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb})
				item.setInfo(type='video', infoLabels=control.metadataClean(meta))
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
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
				else: page = '  [I](%s)[/I]' % url_params.get('page')
				nextMenu = '[COLOR skyblue]' + nextMenu + page + '[/COLOR]'
				u = urlparse(url).netloc.lower()
				if u in self.imdb_link or u in self.trakt_link:
					url = '%s?action=tvshowPage&url=%s' % (sysaddon, quote_plus(url))
				elif u in self.tmdb_link:
					url = '%s?action=tmdbTvshowPage&url=%s' % (sysaddon, quote_plus(url))
				elif u in self.tvmaze_link:
					url = '%s?action=tvmazeTvshowPage&url=%s' % (sysaddon, quote_plus(url))
				item = control.item(label=nextMenu, offscreen=True)
				icon = control.addonNext()
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
				item.setProperty ('SpecialSort', 'bottom')
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		control.content(syshandle, 'tvshows')
		control.directory(syshandle, cacheToDisc=True)
		views.setView('tvshows', {'skin.estuary': 55, 'skin.confluence': 500})

	def addDirectory(self, items, queue=False):
		from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
		control.playlist.clear()
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			content = '' ; control.hide() ; control.notification(title=32002, message=33049)
		sysaddon, syshandle = argv[0], int(argv[1])
		addonThumb = control.addonThumb()
		artPath = control.artPath()
		queueMenu, playRandom, addToLibrary = control.lang(32065), control.lang(32535), control.lang(32551)
		likeMenu, unlikeMenu = control.lang(32186), control.lang(32187)
		for i in items:
			try:
				content = i.get('content', '')
				name = i['name']
				if i['image'].startswith('http'): poster = i['image']
				elif artPath: poster = control.joinPath(artPath, i['image'])
				else: poster = addonThumb
				if content == 'genres':
					icon = control.joinPath(control.genreIconPath(), i['icon']) or 'DefaultFolder.png'
					poster = control.joinPath(control.genrePosterPath(), i['image']) or addonThumb
				else:
					icon = i['icon']
					if icon.startswith('http'): pass
					elif not icon.startswith('Default'): icon = control.joinPath(artPath, icon)
				url = '%s?action=%s' % (sysaddon, i['action'])
				try: url += '&url=%s' % quote_plus(i['url'])
				except: pass
				cm = []
				if (i.get('list_type', '') == 'traktPulicList') and self.traktCredentials:
					liked = traktsync.fetch_liked_list(i['list_id'])
					if not liked:
						cm.append((likeMenu, 'RunPlugin(%s?action=tools_likeList&list_owner=%s&list_name=%s&list_id=%s)' % (sysaddon, quote_plus(i['list_owner']), quote_plus(i['list_name']), i['list_id'])))
					else:
						name = '[COLOR %s][Liked][/COLOR] %s' % (self.highlight_color, name)
						cm.append((unlikeMenu, 'RunPlugin(%s?action=tools_unlikeList&list_owner=%s&list_name=%s&list_id=%s)' % (sysaddon, quote_plus(i['list_owner']), quote_plus(i['list_name']), i['list_id'])))
				cm.append((playRandom, 'RunPlugin(%s?action=play_Random&rtype=show&url=%s)' % (sysaddon, quote_plus(i['url']))))
				if queue: cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem)' % sysaddon))
				try:
					if control.setting('library.service.update') == 'true':
						cm.append((addToLibrary, 'RunPlugin(%s?action=library_tvshowsToLibrary&url=%s&name=%s)' % (sysaddon, quote_plus(i['context']), name)))
				except: pass
				cm.append(('[COLOR ghostwhite]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))

				item = control.item(label=name, offscreen=True)
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'poster': poster, 'thumb': poster, 'fanart': control.addonFanart(), 'banner': poster})
				item.setInfo(type='video', infoLabels={'plot': name})
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		try:
			if not items: raise Exception()
			url = items[0].get('next', '')
			if url == '': raise Exception()
			url_params = dict(parse_qsl(urlsplit(url).query))
			nextMenu = control.lang(32053)
			page = '  [I](%s)[/I]' % url_params.get('page')
			nextMenu = '[COLOR skyblue]' + nextMenu + page + '[/COLOR]'
			icon = control.addonNext()
			url = '%s?action=tv_PublicLists&url=%s' % (sysaddon, quote_plus(url))
			item = control.item(label=nextMenu, offscreen=True)
			item.setProperty('IsPlayable', 'false')
			item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
			item.setProperty ('SpecialSort', 'bottom')
			control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

		skin = control.skin
		if skin == 'skin.arctic.horizon': pass
		elif skin in ('skin.estuary', 'skin.aeon.nox.silvo'): content = ''
		elif skin == 'skin.auramod':
			if content not in ('actors', 'genres'): content = 'addons'
			else: content = ''
		control.content(syshandle, content) # some skins use their own thumb for things like "genres" when content type is set here
		control.directory(syshandle, cacheToDisc=True)