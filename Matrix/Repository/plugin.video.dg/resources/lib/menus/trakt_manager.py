# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime, timedelta
from json import dumps as jsdumps, loads as jsloads
import re
from sys import argv
from urllib.parse import quote_plus, urlencode, parse_qsl, urlparse, urlsplit
from resources.lib.database import cache, metacache, fanarttv_cache, traktsync
from resources.lib.indexers import tmdb as tmdb_indexer, fanarttv
from resources.lib.modules import cleangenre
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules.playcount import getMovieIndicators, getMovieOverlay
from resources.lib.modules import tools
from resources.lib.modules import trakt
from resources.lib.modules import views
from resources.lib.modules import workers


class TraktManager:
	def __init__(self, type='movie', notifications=True):
		self.list = []
		self.lang = control.apiLanguage()['trakt']
		self.imdb_user = control.setting('imdb.user').replace('ur', '')
		self.tmdb_key = control.setting('tmdb.api.key')
		if self.tmdb_key == '' or self.tmdb_key is None:
			self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
		self.tmdb_session_id = control.setting('tmdb.session_id')
		# self.user = str(self.imdb_user) + str(self.tmdb_key)
		self.user = str(self.tmdb_key)

	def watchlistManager(self):
		try:
			control.busy()
			self.list = traktsync.fetch_watch_list('movies_watchlist')
			self.worker()
			self.sort(type='movies.watchlist')
			# self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=False)
			control.hide()
			from resources.lib.windows.traktbasic_manager import TraktBasicManagerXML
			window = TraktBasicManagerXML('traktbasic_manager.xml', control.addonPath(control.addonId()), results=self.list)
			selected_items = window.run()
			del window
			if selected_items:
				# refresh = 'plugin.video.dg' in control.infoLabel('Container.PluginName')
				trakt.removeWatchlistItems('movies', selected_items)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

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