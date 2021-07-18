# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from datetime import datetime, timedelta
from json import dumps as jsdumps, loads as jsloads
import re
import _strptime # import _strptime to workaround python 2 bug with threads
from sys import exit as sysexit, platform as sys_platform
from time import time, sleep
from urllib.parse import quote_plus, parse_qsl, unquote
try: from sqlite3 import dbapi2 as database
except ImportError: from pysqlite2 import dbapi2 as database
from resources.lib.database import metacache, providerscache
from resources.lib.debrid import alldebrid, premiumize, realdebrid
from resources.lib.modules import cleantitle
from resources.lib.modules import control
from resources.lib.modules import debrid
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils
from resources.lib.modules import trakt
from resources.lib.modules import workers
from resources.lib.cloud_scrapers import cloudSources
from fenomscrapers import sources as fs_sources


class Sources:
	def __init__(self):
		self.time = datetime.now()
		self.single_expiry = timedelta(hours=6)
		self.season_expiry = timedelta(hours=48)
		self.show_expiry = timedelta(hours=48)
		self.getConstants()
		self.sources = []
		self.scraper_sources = []
		self.uncached_chosen = False
		self.isPrescrape = False
		self.sourceFile = control.providercacheFile
		self.enable_playnext = control.setting('enable.playnext') == 'true'
		self.dev_mode = control.setting('dev.mode.enable') == 'true'
		self.dev_disable_single = control.setting('dev.disable.single') == 'true'
		# self.dev_disable_single_filter = control.setting('dev.disable.single.filter') == 'true'
		self.dev_disable_season_packs = control.setting('dev.disable.season.packs') == 'true'
		self.dev_disable_season_filter = control.setting('dev.disable.season.filter') == 'true'
		self.dev_disable_show_packs = control.setting('dev.disable.show.packs') == 'true'
		self.dev_disable_show_filter = control.setting('dev.disable.show.filter') == 'true'
		self.extensions = source_utils.supported_video_extensions()
		self.highlight_color = control.getColor(control.setting('highlight.color'))

	def play(self, title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select, rescrape=None):
		gdriveEnabled = control.addon('script.module.fenomscrapers').getSetting('gdrive.cloudflare_url') != ''
		easynewsEnabled = control.addon('script.module.fenomscrapers').getSetting('easynews.user') != ''
		furkEnabled = control.addon('script.module.fenomscrapers').getSetting('furk.user_name') != ''
		if not self.debrid_resolvers and not gdriveEnabled and not easynewsEnabled and not furkEnabled:
			control.sleep(200)
			control.hide()
			control.notification(message=33034)
			return
		try:
			preResolved_nextUrl = control.homeWindow.getProperty('dg.preResolved_nextUrl')
			if preResolved_nextUrl != '':
				log_utils.log('Playing preResolved_nextUrl=%s' % preResolved_nextUrl, level=log_utils.LOGDEBUG)
				control.homeWindow.clearProperty('dg.preResolved_nextUrl')
				try: meta = jsloads(unquote(meta.replace('%22', '\\"')))
				except: pass
				from resources.lib.modules import player
				return player.Player().play_source(title, year, season, episode, imdb, tmdb, tvdb, preResolved_nextUrl, meta)

			if title: title = self.getTitle(title)
			if tvshowtitle: tvshowtitle = self.getTitle(tvshowtitle)
			control.homeWindow.clearProperty(self.metaProperty)
			control.homeWindow.setProperty(self.metaProperty, meta)
			control.homeWindow.clearProperty(self.seasonProperty)
			control.homeWindow.setProperty(self.seasonProperty, season)
			control.homeWindow.clearProperty(self.episodeProperty)
			control.homeWindow.setProperty(self.episodeProperty, episode)
			control.homeWindow.clearProperty(self.titleProperty)
			control.homeWindow.setProperty(self.titleProperty, title)
			control.homeWindow.clearProperty(self.imdbProperty)
			control.homeWindow.setProperty(self.imdbProperty, imdb)
			control.homeWindow.clearProperty(self.tmdbProperty)
			control.homeWindow.setProperty(self.tmdbProperty, tmdb)
			control.homeWindow.clearProperty(self.tvdbProperty)
			control.homeWindow.setProperty(self.tvdbProperty, tvdb)
			p_label = '[COLOR %s]%s (%s)[/COLOR]' % (self.highlight_color, title, year) if tvshowtitle is None else \
			'[COLOR %s]%s (S%02dE%02d)[/COLOR]' % (self.highlight_color, tvshowtitle, int(season), int(episode))
			control.homeWindow.clearProperty(self.labelProperty)
			control.homeWindow.setProperty(self.labelProperty, p_label)

			url = None
			self.mediatype = 'movie'

			try: meta = jsloads(unquote(meta.replace('%22', '\\"')))
			except: pass
			self.meta = meta

			if tvshowtitle is None and control.setting('imdb.year.check') == 'true': # check IMDB. TMDB and Trakt differ on a ratio of 1 in 20 and year is off by 1, some meta titles mismatch
				year, title = self.movie_chk_imdb(imdb, title, year)
			if tvshowtitle is not None: # get "total_seasons" and "season_isAiring" for Pack scrapers. 1st=passed meta, 2nd=matacache check, 3rd=request
				self.mediatype = 'episode'
				self.total_seasons, self.season_isAiring = self.get_season_info(imdb, tmdb, tvdb, meta, season)
			if rescrape: self.clr_item_providers(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered)
			items = providerscache.get(self.getSources, 48, title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered)

			if not items:
				self.url = url
				return self.errorForSources()

			filter = [] ; uncached_items = []
			if control.setting('torrent.remove.uncached') == 'true':
				uncached_items += [i for i in items if re.match(r'^uncached.*torrent', i['source'])]
				filter += [i for i in items if i not in uncached_items]
				if filter: pass
				elif not filter:
					if control.yesnoDialog('No cached torrents returned. Would you like to view the uncached torrents to cache yourself?', '', ''):
						control.cancelPlayback()
						select = '0'
						self.uncached_chosen = True
						filter += uncached_items
				items = filter
				if not items:
					self.url = url
					return self.errorForSources()
			else: uncached_items += [i for i in items if re.match(r'^uncached.*torrent', i['source'])]

			if select is None:
				if episode is not None and self.enable_playnext: select = '1'
				else: select = control.setting('play.mode')

			title = tvshowtitle if tvshowtitle is not None else title
			self.imdb=imdb ; self.tmdb = tmdb ; self.tvdb = tvdb ; self.title = title ; self.year = year
			self.season = season ; self.episode = episode
			self.ids = {'imdb': self.imdb, 'tmdb': self.tmdb, 'tvdb': self.tvdb}
			if len(items) > 0:
				if select == '0':
					control.sleep(200)
					return self.sourceSelect(title, items, uncached_items, self.meta)
				else: url = self.sourcesAutoPlay(items)

			if url == 'close://' or url is None:
				self.url = url
				return self.errorForSources()
			from resources.lib.modules import player
			player.Player().play_source(title, year, season, episode, imdb, tmdb, tvdb, url, self.meta)
		except:
			log_utils.error()
			control.cancelPlayback()

	def sourceSelect(self, title, items, uncached_items, meta):
		try:
			from resources.lib.windows.source_results import SourceResultsXML
			control.hide()
			control.playlist.clear()
			if not items:
				control.sleep(200) ; 	control.hide() ; sysexit()

## - compare meta received to database and use largest(eventually switch to a request to fetch missing db meta for item)
			self.imdb_user = control.setting('imdb.user').replace('ur', '')
			self.tmdb_key = control.setting('tmdb.api.key')
			if not self.tmdb_key: self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
			self.tvdb_key = control.setting('tvdb.api.key')
			if self.mediatype == 'episode': self.user = str(self.imdb_user) + str(self.tvdb_key)
			else: self.user = str(self.tmdb_key)
			self.lang = control.apiLanguage()['tvdb']
			meta1 = dict((k, v) for k, v in iter(meta.items()) if v is not None and v != '') if meta else None
			meta2 = metacache.fetch([{'imdb': self.imdb, 'tmdb': self.tmdb, 'tvdb': self.tvdb}], self.lang, self.user)[0]
			if meta2 != self.ids: meta2 = dict((k, v) for k, v in iter(meta2.items()) if v is not None and v != '')
			if meta1 is not None:
				try:
					if len(meta2) > len(meta1):
						meta2.update(meta1)
						meta = meta2
					else: meta = meta1
				except: log_utils.error()
			else: meta = meta2 if meta2 != self.ids else meta1
##################
			self.poster = meta.get('poster') if meta else ''
			self.fanart = meta.get('fanart') if meta else ''
			self.meta = meta
		except:
			log_utils.error('Error sourceSelect(): ')

		def checkLibMeta(): # check Kodi db for meta for library playback.
			def cleanLibArt(art):
				if not art: return ''
				art = unquote(art.replace('image://', ''))
				if art.endswith('/'): art = art[:-1]
				return art
			try:
				if self.mediatype != 'movie': raise Exception()
				meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "year", "premiered", "genre", "studio", "country", "runtime", "rating", "votes", "mpaa", "director", "writer", "plot", "plotoutline", "tagline", "thumbnail", "art", "file"]}, "id": 1}' % (self.year, str(int(self.year) + 1), str(int(self.year) - 1)))
				meta = jsloads(meta)['result']['movies']
				t = cleantitle.get(self.title.replace('&', 'and'))
				years = [str(self.year), str(int(self.year)+1), str(int(self.year)-1)]
				meta = [i for i in meta if str(i['year']) in years and (t == cleantitle.get(i['title'].replace('&', 'and')) or t == cleantitle.get(i['originaltitle'].replace('&', 'and')))]
				if meta: meta = meta[0]
				else: raise Exception()
				if 'mediatype' not in meta: meta.update({'mediatype': 'movie'})
				if 'duration' not in meta: meta.update({'duration': meta.get('runtime')}) # Trakt scrobble resume needs this for lib playback
				poster = cleanLibArt(meta.get('art').get('poster', '')) or self.poster
				fanart = cleanLibArt(meta.get('art').get('fanart', '')) or self.fanart
				clearart = cleanLibArt(meta.get('art').get('clearart', ''))
				clearlogo = cleanLibArt(meta.get('art').get('clearlogo', ''))
				discart = cleanLibArt(meta.get('art').get('discart'))
				meta.update({'imdb': self.imdb, 'tmdb': self.tmdb, 'tvdb': self.tvdb, 'poster': poster, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'discart': discart})
				return meta
			except:
				log_utils.error()
				meta = ''
			try:
				if self.mediatype != 'episode': raise Exception()
				show_meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "mpaa", "year", "runtime", "thumbnail", "file"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
				show_meta = jsloads(show_meta)['result']['tvshows']
				t = cleantitle.get(self.title.replace('&', 'and'))
				show_meta = [i for i in show_meta if self.year == str(i['year']) and (t == cleantitle.get(i['title'].replace('&', 'and')) or t == cleantitle.get(i['originaltitle'].replace('&', 'and')))]
				if show_meta: show_meta = show_meta[0]
				else: raise Exception()
				tvshowid = show_meta['tvshowid']
				meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params":{ "tvshowid": %d, "filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "season", "episode", "showtitle", "firstaired", "runtime", "rating", "director", "writer", "plot", "thumbnail", "art", "file"]}, "id": 1}' % (tvshowid, self.season, self.episode))
				meta = jsloads(meta)['result']['episodes']
				if meta: meta = meta[0]
				else: raise Exception()
				if 'mediatype' not in meta: meta.update({'mediatype': 'episode'})
				if 'duration' not in meta: meta.update({'duration': meta.get('runtime')}) # Trakt scrobble resume needs this for lib playback
				if 'mpaa' not in meta: meta.update({'mpaa': show_meta.get('mpaa')})
				if 'premiered' not in meta: meta.update({'premiered': meta.get('firstaired')})
				if 'year' not in meta: meta.update({'year': meta.get('firstaired')[:4]})
				poster = cleanLibArt(meta.get('art').get('season.poster', '')) or self.poster
				fanart = cleanLibArt(meta.get('art').get('tvshow.fanart', '')) or self.poster
				clearart = cleanLibArt(meta.get('art').get('tvshow.clearart', ''))
				clearlogo = cleanLibArt(meta.get('art').get('tvshow.clearlogo', ''))
				discart = cleanLibArt(meta.get('art').get('discart'))
				meta.update({'imdb': self.imdb, 'tmdb': self.tmdb, 'tvdb': self.tvdb, 'poster': poster, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'discart': discart})
				return meta
			except:
				log_utils.error()
				meta = ''
		if self.meta is None or 'videodb' in control.infoLabel('ListItem.FolderPath'):
			self.meta = checkLibMeta()

		try:
			def sourcesDirMeta(metadata): # pass skin minimal meta needed
				if not metadata: return metadata
				allowed = ['mediatype', 'imdb', 'tmdb', 'tvdb', 'poster', 'season_poster', 'fanart', 'clearart', 'clearlogo', 'discart', 'thumb', 'title', 'tvshowtitle', 'year', 'premiered', 'rating', 'plot', 'duration', 'mpaa', 'season', 'episode']
				return {k: v for k, v in iter(metadata.items()) if k in allowed}
			self.meta = sourcesDirMeta(self.meta)

			if items == uncached_items:
				from resources.lib.windows.uncached_results import UncachedResultsXML
				window = UncachedResultsXML('uncached_results.xml', control.addonPath(control.addonId()), uncached=uncached_items, meta=self.meta)
			else: window = SourceResultsXML('source_results.xml', control.addonPath(control.addonId()), results=items, uncached=uncached_items, meta=self.meta)
			action, chosen_source = window.run()
			del window
			if action == 'play_Item' and self.uncached_chosen != True:
				return self.playItem(title, items, chosen_source.getProperty('dg.source_dict'), self.meta)
			else:
				control.cancelPlayback()
		except:
			log_utils.error('Error sourceSelect(): ')
			control.cancelPlayback()

	def playItem(self, title, items, chosen_source, meta):
		try:
			try: items = jsloads(items)
			except: pass
			try: meta = jsloads(meta)
			except: pass

			year = meta['year'] if 'year' in meta else None # year to be shows year, not season year.
			season = meta['season'] if 'season' in meta else None
			episode = meta['episode'] if 'episode' in meta else None
			imdb = meta['imdb'] if 'imdb' in meta else None
			tmdb = meta['tmdb'] if 'tmdb' in meta else None
			tvdb = meta['tvdb'] if 'tvdb' in meta else None

			try:
				chosen_source = jsloads(chosen_source)
				source_index = items.index(chosen_source[0])
				source_len = len(items)
				next_end = min(source_len, source_index+41)
				sources_next = items[source_index+1:next_end]
				sources_prev = [] if next_end < source_len else items[0:41-(source_len-source_index)]
				items = [i for i in chosen_source + sources_next + sources_prev]
			except:
				log_utils.error()
			header = control.homeWindow.getProperty(self.labelProperty) + ': Resolving...'
			progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
			progressDialog.create(header, '')
			for i in range(len(items)):
				try:
					src_provider = items[i]['debrid'] if items[i].get('debrid') else ('%s - %s' % (items[i]['source'], items[i]['provider']))
					label = '[COLOR %s]%s[CR]%s[CR]%s[/COLOR]' % (self.highlight_color, src_provider.upper(), items[i]['name'], str(round(items[i]['size'], 2)) + ' GB') # using "[CR]" has some weird delay with progressDialog.update() at times
					control.sleep(100)
					try:
						if progressDialog.iscanceled(): break
						progressDialog.update(int((100 / float(len(items))) * i), label)
					except: progressDialog.update(int((100 / float(len(items))) * i), '[COLOR %s]Resolving...[/COLOR]%s' % (self.highlight_color, items[i]['name']))

					w = workers.Thread(self.sourcesResolve, items[i])
					w.start()
					for x in range(40):
						try:
							if control.monitor.abortRequested(): return sysexit()
							if progressDialog.iscanceled():
								control.notification(message=32398)
								control.cancelPlayback()
								progressDialog.close()
								del progressDialog
								return
						except: pass
						if not w.is_alive(): break
						sleep(0.5)

					if not self.url: raise Exception()
					if not any(x in self.url.lower() for x in self.extensions):
						log_utils.log('Playback not supported for (playItem()): %s' % self.url, level=log_utils.LOGWARNING)
						raise Exception()
					log_utils.log('Playing url from playItem(): %s' % self.url, level=log_utils.LOGDEBUG)
					try: progressDialog.close()
					except: pass
					del progressDialog
					from resources.lib.modules import player
					player.Player().play_source(title, year, season, episode, imdb, tmdb, tvdb, self.url, meta)
					return self.url
				except:
					log_utils.error()
			try: progressDialog.close()
			except: pass
			del progressDialog
			self.errorForSources()
		except:
			log_utils.error('Error playItem: ')

	def getSources(self, title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta=None, preScrape=False):
		if preScrape:
			self.isPrescrape = True
			if tvshowtitle is not None:
				self.mediatype = 'episode'
				self.meta = meta
				self.total_seasons, self.season_isAiring = self.get_season_info(imdb, tmdb, tvdb, meta, season)
			return self.getSources_silent(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered)
		else:
			return self.getSources_dialog(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered)

	def getSources_silent(self, title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, timeout=60):
		try:
			self.prepareSources()
			sourceDict = self.sourceDict
			sourceDict = [(i[0], i[1], getattr(i[1], 'tvshow', None)) for i in sourceDict]
			sourceDict = [(i[0], i[1]) for i in sourceDict if i[2] is not None]
			if control.setting('cf.disable') == 'true': sourceDict = [(i[0], i[1]) for i in sourceDict if not any(x in i[0] for x in self.sourcecfDict)]
			sourceDict = [(i[0], i[1], i[1].priority) for i in sourceDict]
			sourceDict = sorted(sourceDict, key=lambda i: i[2]) # sorted by scraper priority num
			aliases = []
			try:
				# meta = jsloads(unquote(control.homeWindow.getProperty(self.metaProperty).replace('%22', '\\"')))
				meta = self.meta
				aliases = meta.get('aliases', [])
			except: pass

			threads = []
			from fenomscrapers import pack_sources
			self.packDict = providerscache.get(pack_sources, 192)
			trakt_aliases = self.getAliasTitles(imdb, 'episode')
			try: aliases.extend([i for i in trakt_aliases if not i in aliases]) # combine TMDb and Trakt aliases
			except: pass
			aliases = jsdumps(aliases)
			for i in sourceDict:
				threads.append(workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, aliases, premiered, i[0], i[1]))

			s = [i[0] + (i[1],) for i in zip(sourceDict, threads)]
			s = [(i[3].getName(), i[0], i[2]) for i in s]
			sourcelabelDict = dict([(i[0], i[1].upper()) for i in s])
			[i.start() for i in threads]

			start_time = time()
			end_time = start_time + timeout
		except:
			log_utils.error()
			return

		while True:
			try:
				if control.monitor.abortRequested(): return sysexit()
				try:
					info = [sourcelabelDict[x.getName()] for x in threads if x.is_alive() == True]
					if len(info) == 0: break
					current_time = time()
					if end_time < current_time: break
				except:
					log_utils.error()
					break
				control.sleep(100)
			except:
				log_utils.error()
		del threads[:] # Make sure any remaining providers are stopped.
		self.sources.extend(self.scraper_sources)
		if len(self.sources) > 0:
			self.sourcesFilter()
		return self.sources

	def getSources_dialog(self, title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, timeout=60):
		try:
			progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
			header = control.homeWindow.getProperty(self.labelProperty) + ': Scraping...'
			progressDialog.create(header, '')

			self.prepareSources()
			sourceDict = self.sourceDict
			progressDialog.update(0, control.lang(32600))

			content = 'movie' if tvshowtitle is None else 'episode'
			if content == 'movie': sourceDict = [(i[0], i[1], getattr(i[1], 'movie', None)) for i in sourceDict]
			else: sourceDict = [(i[0], i[1], getattr(i[1], 'tvshow', None)) for i in sourceDict]
			sourceDict = [(i[0], i[1]) for i in sourceDict if i[2] is not None]
			if control.setting('cf.disable') == 'true': sourceDict = [(i[0], i[1]) for i in sourceDict if not any(x in i[0] for x in self.sourcecfDict)]
			sourceDict = [(i[0], i[1], i[1].priority) for i in sourceDict]
			sourceDict = sorted(sourceDict, key=lambda i: i[2]) # sorted by scraper priority num
			aliases = []
			try:
				# meta = jsloads(unquote(control.homeWindow.getProperty(self.metaProperty).replace('%22', '\\"')))
				meta = self.meta
				aliases = meta.get('aliases', [])
			except: pass
			threads = []
			if content == 'movie':
				trakt_aliases = self.getAliasTitles(imdb, content)
				try: aliases.extend([i for i in trakt_aliases if not i in aliases]) # combine TMDb and Trakt aliases
				except: pass
				aliases = jsdumps(aliases)
				for i in sourceDict:
					threads.append(workers.Thread(self.getMovieSource, title, aliases, year, imdb, i[0], i[1]))
			else:
				from fenomscrapers import pack_sources
				self.packDict = providerscache.get(pack_sources, 192)
				trakt_aliases = self.getAliasTitles(imdb, content)
				try: aliases.extend([i for i in trakt_aliases if not i in aliases]) # combine TMDb and Trakt aliases
				except: pass
				aliases = jsdumps(aliases)
				for i in sourceDict:
					threads.append(workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, aliases, premiered, i[0], i[1]))

			s = [i[0] + (i[1],) for i in zip(sourceDict, threads)]
			s = [(i[3].getName(), i[0], i[2]) for i in s]
			sourcelabelDict = dict([(i[0], i[1].upper()) for i in s])
			[i.start() for i in threads]

			sdc = control.getColor(control.setting('scraper.dialog.color'))
			string1 = control.lang(32404) % (self.highlight_color, sdc, '%s') # msgid "[COLOR %s]Time elapsed:[/COLOR]  [COLOR %s]%s seconds[/COLOR]"
			string3 = control.lang(32406) % (self.highlight_color, sdc, '%s') # msgid "[COLOR %s]Remaining providers:[/COLOR] [COLOR %s]%s[/COLOR]"
			string4 = control.lang(32407) % (self.highlight_color, sdc, '%s') # msgid "[COLOR %s]Unfiltered Total: [/COLOR]  [COLOR %s]%s[/COLOR]"

			try: timeout = int(control.setting('scrapers.timeout'))
			except: pass
			start_time = time()
			end_time = start_time + timeout
			quality = control.setting('hosts.quality') or '0'
			line1 = line2 = line3 = ""
			terminate_onCloud = str(control.setting('terminate.onCloud.sources'))
			pre_emp = str(control.setting('preemptive.termination'))
			pre_emp_limit = int(control.setting('preemptive.limit'))
			pre_emp_res = str(control.setting('preemptive.res'))
			source_4k = source_1080 = source_720 = source_sd = total = 0
			total_format = '[COLOR %s][B]%s[/B][/COLOR]'
			pdiag_format = '[COLOR %s]4K:[/COLOR]  %s  |  [COLOR %s]1080p:[/COLOR]  %s  |  [COLOR %s]720p:[/COLOR]  %s  |  [COLOR %s]SD:[/COLOR]  %s' % \
				(self.highlight_color, '%s', self.highlight_color, '%s', self.highlight_color, '%s', self.highlight_color, '%s')
			control.hide()
		except:
			log_utils.error()
			try: progressDialog.close()
			except: pass
			del progressDialog
			return

		while True:
			try:
				if control.monitor.abortRequested(): return sysexit()
				try:
					if progressDialog.iscanceled(): break
				except: pass

				if terminate_onCloud == 'true':
					if len([e for e in self.scraper_sources if e['source'] == 'cloud']) > 0: break
				if pre_emp == 'true':
					if pre_emp_res == '0':
						if (source_4k) >= pre_emp_limit: break
					elif pre_emp_res == '1':
						if (source_1080) >= pre_emp_limit: break
					elif pre_emp_res == '2':
						if (source_720) >= pre_emp_limit: break
					elif pre_emp_res == '3':
						if (source_sd) >= pre_emp_limit: break
					else:
						if (source_sd) >= pre_emp_limit: break

				if quality == '0':
					source_4k = len([e for e in self.scraper_sources if e['quality'] == '4K'])
					source_1080 = len([e for e in self.scraper_sources if e['quality'] == '1080p'])
					source_720 = len([e for e in self.scraper_sources if e['quality'] in ['720p', 'HD']])
					source_sd = len([e for e in self.scraper_sources if e['quality'] in ['SD', 'SCR', 'CAM']])
				elif quality == '1':
					source_1080 = len([e for e in self.scraper_sources if e['quality'] == '1080p'])
					source_720 = len([e for e in self.scraper_sources if e['quality'] in ['720p', 'HD']])
					source_sd = len([e for e in self.scraper_sources if e['quality'] in ['SD', 'SCR', 'CAM']])
				elif quality == '2':
					source_720 = len([e for e in self.scraper_sources if e['quality'] in ['720p', 'HD']])
					source_sd = len([e for e in self.scraper_sources if e['quality'] in ['SD', 'SCR', 'CAM']])
				else:
					source_sd = len([e for e in self.scraper_sources if e['quality'] in ['SD', 'SCR', 'CAM']])
				total = source_4k + source_1080 + source_720 + source_sd

				source_4k_label = total_format % ('red', source_4k) if source_4k == 0 else total_format % (sdc, source_4k)
				source_1080_label = total_format % ('red', source_1080) if source_1080 == 0 else total_format % (sdc, source_1080)
				source_720_label = total_format % ('red', source_720) if source_720 == 0 else total_format % (sdc, source_720)
				source_sd_label = total_format % ('red', source_sd) if source_sd == 0 else total_format % (sdc, source_sd)
				source_total_label = total_format % ('red', total) if total == 0 else total_format % (sdc, total)
				try:
					info = [sourcelabelDict[x.getName()] for x in threads if x.is_alive() == True]
					line1 = pdiag_format % (source_4k_label, source_1080_label, source_720_label, source_sd_label)
					line2 = string4 % source_total_label + '     ' + string1 % round(time() - start_time, 1)
					if len(info) > 6: line3 = string3 % str(len(info))
					elif len(info) > 0: line3 = string3 % (', '.join(info))
					else: break
					current_time = time()
					current_progress = current_time - start_time
					percent = int((current_progress / float(timeout)) * 100)
					if progressDialog != control.progressDialogBG: progressDialog.update(max(1, percent), line1 + '[CR]' + line2 + '[CR]' + line3)
					else: progressDialog.update(max(1, percent), line1 + '  ' + string3 % str(len(info)))
					if end_time < current_time: break
				except:
					log_utils.error()
					break
				control.sleep(100)
			except:
				log_utils.error()
		try: progressDialog.close()
		except: pass
		del progressDialog
		del threads[:] # Make sure any remaining providers are stopped.
		self.sources.extend(self.scraper_sources)
		if len(self.sources) > 0: self.sourcesFilter()
		return self.sources

	def preResolve(self, next_sources, next_meta):
		try:
			control.homeWindow.setProperty(self.metaProperty, jsdumps(next_meta))
			if control.setting('autoplay.sd') == 'true': next_sources = [i for i in next_sources if not i['quality'] in ['4K', '1080p', '720p']]
			uncached_filter = [i for i in next_sources if re.match(r'^uncached.*torrent', i['source'])]
			next_sources = [i for i in next_sources if i not in uncached_filter]
		except:
			log_utils.error()
			return control.homeWindow.clearProperty('dg.preResolved_nextUrl')
		u = ''
		for i in range(len(next_sources)):
			try:
				control.sleep(100)
				try:
					if control.monitor.abortRequested(): return sysexit()
					url = self.sourcesResolve(next_sources[i])
					if not url:
						log_utils.log('preResolve failed for : next_sources[i]=%s' % str(next_sources[i]), level=log_utils.LOGWARNING)
						continue
					if not any(x in url.lower() for x in self.extensions):
						log_utils.log('preResolve Playback not supported for (sourcesAutoPlay()): %s' % url, level=log_utils.LOGWARNING)
						raise Exception()
					if not u: u = url
					log_utils.log('PreResolved url : %s' % url, level=log_utils.LOGDEBUG)
					if url: break
				except: pass
			except:
				log_utils.error()
		control.homeWindow.setProperty('dg.preResolved_nextUrl', u)

	def prepareSources(self):
		try:
			control.makeFile(control.dataPath)
			dbcon = database.connect(self.sourceFile)
			dbcur = dbcon.cursor()
			dbcur.execute('''CREATE TABLE IF NOT EXISTS rel_url (source TEXT, imdb_id TEXT, season TEXT, episode TEXT, rel_url TEXT, UNIQUE(source, imdb_id, season, episode));''')
			dbcur.execute('''CREATE TABLE IF NOT EXISTS rel_src (source TEXT, imdb_id TEXT, season TEXT, episode TEXT, hosts TEXT, added TEXT, UNIQUE(source, imdb_id, season, episode));''')
			dbcur.connection.commit()
		except:
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()

	def getMovieSource(self, title, aliases, year, imdb, source, call):
		try:
			dbcon = database.connect(self.sourceFile, timeout=60)
			dbcur = dbcon.cursor()
		except: pass
		''' Fix to stop items passed with a 0 IMDB id pulling old unrelated sources from the database. '''
		if not imdb:
			try:
				for table in ["rel_src", "rel_url"]: dbcur.execute('''DELETE FROM {} WHERE (source=? AND imdb_id='' AND season='' AND episode='')'''.format(table), (source, ))
				dbcur.connection.commit()
			except:
				log_utils.error()
		try:
			sources = []
			db_movie = dbcur.execute('''SELECT * FROM rel_src WHERE (source=? AND imdb_id=? AND season='' AND episode='')''', (source, imdb)).fetchone()
			if db_movie:
				timestamp = control.datetime_workaround(str(db_movie[5]), '%Y-%m-%d %H:%M:%S.%f', False)
				db_movie_valid = abs(self.time - timestamp) < self.single_expiry
				if db_movie_valid:
					sources = eval(db_movie[4])
					return self.scraper_sources.extend(sources)
		except:
			log_utils.error()
		try:
			url = None
			url = dbcur.execute('''SELECT * FROM rel_url WHERE (source=? AND imdb_id=? AND season='' AND episode='')''', (source, imdb)).fetchone()
			if url: url = eval(url[4])
		except:
			log_utils.error()
		try:
			if not url: url = call.movie(imdb, title, aliases, year)
			if url:
				dbcur.execute('''INSERT OR REPLACE INTO rel_url Values (?, ?, ?, ?, ?)''', (source, imdb, '', '', repr(url)))
				dbcur.connection.commit()
		except:
			log_utils.error()
		try:
			sources = []
			sources = call.sources(url, self.hostprDict)
			if sources:
				sources = [jsloads(t) for t in set(jsdumps(d, sort_keys=True) for d in sources)]
				self.scraper_sources.extend(sources)
				dbcur.execute('''INSERT OR REPLACE INTO rel_src Values (?, ?, ?, ?, ?, ?)''', (source, imdb, '', '', repr(sources), datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
				dbcur.connection.commit()
		except:
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()

	def getEpisodeSource(self, title, year, imdb, tvdb, season, episode, tvshowtitle, aliases, premiered, source, call):
		try:
			dbcon = database.connect(self.sourceFile, timeout=60)
			dbcur = dbcon.cursor()
		except: pass
		''' Fix to stop items passed with a 0 IMDB id pulling old unrelated sources from the database. '''
		if not imdb:
			try:
				for table in ["rel_src", "rel_url"]: dbcur.execute('''DELETE FROM {} WHERE (source=? AND imdb_id='' AND season=? AND episode=?)'''.format(table), (source, season, episode))
				dbcur.execute('''DELETE FROM rel_src WHERE (source = ? AND imdb_id = '' AND season = ? AND episode = '')''', (source, season))
				for table in ["rel_src", "rel_url"]: dbcur.execute('''DELETE FROM {} WHERE (source=? AND imdb_id='' AND season='' AND episode='')'''.format(table), (source, ))
				dbcur.connection.commit()
			except:
				log_utils.error()
		try: # singleEpisodes db check
			db_singleEpisodes_valid = False
			if self.dev_mode and self.dev_disable_single: raise Exception()
			sources = []
			db_singleEpisodes = dbcur.execute('''SELECT * FROM rel_src WHERE (source=? AND imdb_id=? AND season=? AND episode=?)''', (source, imdb, season, episode)).fetchone()
			if db_singleEpisodes:
				timestamp = control.datetime_workaround(str(db_singleEpisodes[5]), '%Y-%m-%d %H:%M:%S.%f', False)
				db_singleEpisodes_valid = abs(self.time - timestamp) < self.single_expiry
				if db_singleEpisodes_valid:
					sources = eval(db_singleEpisodes[4])
					self.scraper_sources.extend(sources)
		except:
			log_utils.error()
		try: # seasonPacks db check
			db_seasonPacks_valid = False
			if self.season_isAiring == 'true': raise Exception()
			if self.dev_mode and self.dev_disable_season_packs: raise Exception()
			sources = []
			db_seasonPacks = dbcur.execute('''SELECT * FROM rel_src WHERE (source=? AND imdb_id=? AND season=? AND episode='')''', (source, imdb, season)).fetchone()
			if db_seasonPacks:
				timestamp = control.datetime_workaround(str(db_seasonPacks[5]), '%Y-%m-%d %H:%M:%S.%f', False)
				db_seasonPacks_valid = abs(self.time - timestamp) < self.season_expiry
				if db_seasonPacks_valid:
					sources = eval(db_seasonPacks[4])
					self.scraper_sources.extend(sources)
		except:
			log_utils.error()
		try: # showPacks db check
			db_showPacks_valid = False
			if self.season_isAiring == 'true': raise Exception()
			if self.dev_mode and self.dev_disable_show_packs: raise Exception()
			sources = []
			db_showPacks = dbcur.execute('''SELECT * FROM rel_src WHERE (source=? AND imdb_id=? AND season='' AND episode='')''', (source, imdb)).fetchone()
			if db_showPacks:
				timestamp = control.datetime_workaround(str(db_showPacks[5]), '%Y-%m-%d %H:%M:%S.%f', False)
				db_showPacks_valid = abs(self.time - timestamp) < self.show_expiry
				if db_showPacks_valid:
					sources = eval(db_showPacks[4])
					sources = [i for i in sources if i.get('last_season') >= int(season)] # filter out range items that do not apply to current season
					self.scraper_sources.extend(sources)
					if db_singleEpisodes_valid and db_seasonPacks_valid:
						return self.scraper_sources
		except:
			log_utils.error()
		try:
			url = None
			url = dbcur.execute('''SELECT * FROM rel_url WHERE (source=? AND imdb_id=? AND season='' AND episode='')''', (source, imdb)).fetchone()
			if url: url = eval(url[4])
		except:
			log_utils.error()
		try:
			if not url: url = call.tvshow(imdb, tvdb, tvshowtitle, aliases, year)
			if url:
				dbcur.execute('''INSERT OR REPLACE INTO rel_url Values (?, ?, ?, ?, ?)''', (source, imdb, '', '', repr(url)))
				dbcur.connection.commit()
		except:
			log_utils.error()
		try:
			ep_url = None
			ep_url = dbcur.execute('''SELECT * FROM rel_url WHERE (source=? AND imdb_id=? AND season=? AND episode=?)''', (source, imdb, season, episode)).fetchone()
			if ep_url: ep_url = eval(ep_url[4])
		except:
			log_utils.error()
		try:
			if url:
				if not ep_url: ep_url = call.episode(url, imdb, tvdb, title, premiered, season, episode)
				if ep_url:
					dbcur.execute('''INSERT OR REPLACE INTO rel_url Values (?, ?, ?, ?, ?)''', (source, imdb, season, episode, repr(ep_url)))
					dbcur.connection.commit()
		except:
			log_utils.error()
		try: # singleEpisodes scraper call
			if self.dev_mode and self.dev_disable_single: raise Exception()
			if db_singleEpisodes_valid: raise Exception()
			sources = []
			sources = call.sources(ep_url, self.hostprDict)
			if sources:
				sources = [jsloads(t) for t in set(jsdumps(d, sort_keys=True) for d in sources)]
				self.scraper_sources.extend(sources)
				dbcur.execute('''INSERT OR REPLACE INTO rel_src Values (?, ?, ?, ?, ?, ?)''', (source, imdb, season, episode, repr(sources), datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
				dbcur.connection.commit()
		except:
			log_utils.error()
		try: # seasonPacks scraper call
			if self.dev_mode and self.dev_disable_season_packs: raise Exception()
			if self.season_isAiring == 'true': raise Exception()
			if self.packDict and source in self.packDict:
				if db_seasonPacks_valid: raise Exception()
				sources = []
				sources = call.sources_packs(ep_url, self.hostprDict, bypass_filter=self.dev_disable_season_filter)
				if sources:
					sources = [jsloads(t) for t in set(jsdumps(d, sort_keys=True) for d in sources)]
					self.scraper_sources.extend(sources)
					dbcur.execute('''INSERT OR REPLACE INTO rel_src Values (?, ?, ?, ?, ?, ?)''', (source, imdb, season,'', repr(sources), datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
					dbcur.connection.commit()
		except:
			log_utils.error()
		try: # showPacks scraper call
			if self.dev_mode and self.dev_disable_show_packs: raise Exception()
			if self.season_isAiring == 'true': raise Exception() # need a "series_isAiring" to skip
			if self.packDict and source in self.packDict:
				if db_showPacks_valid: raise Exception()
				sources = []
				sources = call.sources_packs(ep_url, self.hostprDict, search_series=True, total_seasons=self.total_seasons, bypass_filter=self.dev_disable_show_filter)
				if sources:
					sources = [jsloads(t) for t in set(jsdumps(d, sort_keys=True) for d in sources)]
					sources = [i for i in sources if i.get('last_season') >= int(season)] # filter out range items that do not apply to current season
					self.scraper_sources.extend(sources)
					dbcur.execute('''INSERT OR REPLACE INTO rel_src Values (?, ?, ?, ?, ?, ?)''', (source, imdb, '', '', repr(sources), datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
					dbcur.connection.commit()
		except:
			log_utils.error()
		finally:
			dbcon.close() ; dbcon.close()

	def sourcesFilter(self):
		if not self.isPrescrape: control.busy()
		quality = control.setting('hosts.quality') or '0'
		if control.setting('remove.duplicates') == 'true': self.sources = self.filter_dupes()
		if self.mediatype == 'movie':
			if control.setting('source.enable.msizelimit') == 'true':
				try:
					movie_minSize = float(control.setting('source.min.moviesize'))
					movie_maxSize = float(control.setting('source.max.moviesize'))
					self.sources = [i for i in self.sources if (i.get('size', 0) >= movie_minSize and i.get('size', 0) <= movie_maxSize)]
				except:
					log_utils.error()
		else:
			try: self.sources = self.calc_pack_size()
			except: pass
			if control.setting('source.enable.esizelimit') == 'true':
				try:
					episode_minSize = float(control.setting('source.min.epsize'))
					episode_maxSize = float(control.setting('source.max.epsize'))
					self.sources = [i for i in self.sources if (i.get('size', 0) >= episode_minSize and i.get('size', 0) <= episode_maxSize)]
				except:
					log_utils.error()
		if control.setting('remove.hevc') == 'true':
			self.sources = [i for i in self.sources if 'HEVC' not in i.get('info', '')] # scrapers write HEVC to info
		if control.setting('remove.hdr') == 'true':
			filter = [i for i in self.sources if '.sdr' not in i.get('name_info')]
			filter = [i for i in filter if any(value in i.get('name_info') for value in source_utils.HDR)]
			self.sources = [i for i in self.sources if i not in filter]
		if control.setting('remove.dolby.vision') == 'true':
			self.sources = [i for i in self.sources if not any(value in i.get('name_info', '') for value in source_utils.DOLBY_VISION)]
		if control.setting('remove.cam.sources') == 'true':
			self.sources = [i for i in self.sources if i['quality'] != 'CAM']
		if control.setting('remove.sd.sources') == 'true':
			if any(i for i in self.sources if any(value in i['quality'] for value in ['4K', '1080p', '720p'])): #only remove SD if better quality does exist
				self.sources = [i for i in self.sources if i['quality'] != 'SD']
		if control.setting('remove.3D.sources') == 'true':
			self.sources = [i for i in self.sources if '3D' not in i.get('info', '')] # scrapers write 3D to info

		local = [i for i in self.sources if 'local' in i and i['local'] is True] # for library and videoscraper (skips cache check)
		self.sources = [i for i in self.sources if not i in local]
		direct = [i for i in self.sources if i['direct'] == True] # acct scrapers (skips cache check)
		self.sources = [i for i in self.sources if not i in direct]

		from copy import deepcopy
		deepcopy_sources = deepcopy(self.sources)
		deepcopy_sources = [i for i in deepcopy_sources if 'magnet:' in i['url']]
		threads = [] ; self.filter = []
		valid_hosters = set([i['source'] for i in self.sources])

		def checkStatus(function, debrid_name, valid_hoster):
			try:
				cached = None
				if deepcopy_sources: cached = function(deepcopy_sources)
				if cached: self.filter += [dict(list(i.items()) + [('debrid', debrid_name)]) for i in cached if 'magnet:' in i['url']]
				self.filter += [dict(list(i.items()) + [('debrid', debrid_name)]) for i in self.sources if i['source'] in valid_hoster and 'magnet:' not in i['url']]
			except:
				log_utils.error()

		for d in self.debrid_resolvers:
			if d.name == 'Premiumize.me' and control.setting('premiumize.enable') == 'true':
				try:
					valid_hoster = [i for i in valid_hosters if d.valid_url(i)]
					threads.append(workers.Thread(checkStatus, self.pm_cache_chk_list, d.name, valid_hoster))
				except:
					log_utils.error()
			if d.name == 'Real-Debrid' and control.setting('realdebrid.enable') == 'true':
				try:
					valid_hoster = [i for i in valid_hosters if d.valid_url(i)]
					threads.append(workers.Thread(checkStatus, self.rd_cache_chk_list, d.name, valid_hoster))
				except:
					log_utils.error()
			if d.name == 'AllDebrid' and control.setting('alldebrid.enable') == 'true':
				try:
					valid_hoster = [i for i in valid_hosters if d.valid_url(i)]
					threads.append(workers.Thread(checkStatus, self.ad_cache_chk_list, d.name, valid_hoster))
				except:
					log_utils.error()
		if threads:
			[i.start() for i in threads]
			[i.join() for i in threads]
		self.filter += direct
		self.filter += local
		self.sources = self.filter

		if control.setting('sources.group.sort') == '1':
			torr_filter = []
			torr_filter += [i for i in self.sources if 'torrent' in i['source']]  #torrents first
			if control.setting('sources.size.sort') == 'true': torr_filter.sort(key=lambda k: k.get('size', 0), reverse=True)
			aact_filter = []
			aact_filter += [i for i in self.sources if i['direct'] == True]  #account scrapers and local/library next
			if control.setting('sources.size.sort') == 'true': aact_filter.sort(key=lambda k: k.get('size', 0), reverse=True)
			prem_filter = []
			prem_filter += [i for i in self.sources if 'torrent' not in i['source'] and i['debridonly'] is True]  #prem.hosters last
			if control.setting('sources.size.sort') == 'true': prem_filter.sort(key=lambda k: k.get('size', 0), reverse=True)
			self.sources = torr_filter
			self.sources += aact_filter
			self.sources += prem_filter

		elif control.setting('sources.size.sort') == 'true':
			filter = []
			filter += [i for i in self.sources]
			filter.sort(key=lambda k: k.get('size', 0), reverse=True)
			self.sources = filter

		filter = []
		if quality in ['0']: filter += [i for i in self.sources if i['quality'] == '4K']
		if quality in ['0', '1']: filter += [i for i in self.sources if i['quality'] == '1080p']
		if quality in ['0', '1', '2']: filter += [i for i in self.sources if i['quality'] == '720p']
		filter += [i for i in self.sources if i['quality'] == 'SCR']
		filter += [i for i in self.sources if i['quality'] == 'SD']
		filter += [i for i in self.sources if i['quality'] == 'CAM']
		self.sources = filter

		filter = [] # new filter to place cloud files first
		filter += [i for i in self.sources if i['source'] == 'cloud']
		filter += [i for i in self.sources if i['source'] != 'cloud']
		self.sources = filter

		self.sources = self.sources[:4000]
		control.hide()
		return self.sources

	def filter_dupes(self):
		filter = []
		log_dupes = control.setting('remove.duplicates.logging') == 'false'
		for i in self.sources:
			larger = False
			a = i['url'].lower()
			for sublist in filter:
				try:
					if i['source'] == 'cloud':
						break
					b = sublist['url'].lower()
					if 'magnet:' in a:
						if i['hash'].lower() in b:
							if len(sublist['name']) > len(i['name']): # keep matching hash with longer name, possible more file info.
								larger = True
								break
							filter.remove(sublist)
							if log_dupes: log_utils.log('Removing %s - %s (DUPLICATE TORRENT) ALREADY IN :: %s' % (sublist['provider'], b, i['provider']), level=log_utils.LOGDEBUG)
							break
					elif a == b:
						filter.remove(sublist)
						if log_dupes: log_utils.log('Removing %s - %s (DUPLICATE LINK) ALREADY IN :: %s' % (sublist['source'], i['url'], i['provider']), level=log_utils.LOGDEBUG)
						break
				except:
					log_utils.error('Error filter_dupes: ')
			if not larger: #sublist['name'] len() was larger so do not append
				filter.append(i)
		header = control.homeWindow.getProperty(self.labelProperty)
		if not self.enable_playnext:
			control.notification(title=header, message='Removed %s duplicate sources from list' % (len(self.sources) - len(filter)))
		log_utils.log('Removed %s duplicate sources for (%s) from list' % (len(self.sources) - len(filter), control.homeWindow.getProperty(self.labelProperty)), level=log_utils.LOGDEBUG)
		return filter

	def sourcesAutoPlay(self, items):
		if control.setting('autoplay.sd') == 'true': items = [i for i in items if not i['quality'] in ['4K', '1080p', '720p']]
		u = None
		header = control.homeWindow.getProperty(self.labelProperty) + ': Resolving...'
		try:
			progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
			progressDialog.create(header, '')
		except: pass
		for i in range(len(items)):
			try:
				src_provider = items[i]['debrid'] if items[i].get('debrid') else ('%s - %s' % (items[i]['source'], items[i]['provider']))
				label = '[COLOR %s]%s[CR]%s[CR]%s[/COLOR]' % (self.highlight_color, src_provider.upper(), items[i]['name'], str(round(items[i]['size'], 2)) + ' GB') # using "[CR]" has some weird delay with progressDialog.update() at times
				control.sleep(100)
				try:
					if progressDialog.iscanceled(): break
					progressDialog.update(int((100 / float(len(items))) * i), label)
				except: progressDialog.update(int((100 / float(len(items))) * i), '[COLOR %s]Resolving...[/COLOR]%s' % (self.highlight_color, items[i]['name']))
				try:
					if control.monitor.abortRequested(): return sysexit()
					url = self.sourcesResolve(items[i])
					if not any(x in url.lower() for x in self.extensions):
						log_utils.log('Playback not supported for (sourcesAutoPlay()): %s' % url, level=log_utils.LOGWARNING)
						raise Exception()
					if not u: u = url
					log_utils.log('Playing url from (sourcesAutoPlay()): %s' % url, level=log_utils.LOGDEBUG)
					if url: break
				except: pass
			except:
				log_utils.error()
		try: progressDialog.close()
		except: pass
		del progressDialog
		return u

	def sourcesResolve(self, item):
		try:
			url = item['url']
			self.url = None
			debrid_provider = item['debrid'] if item.get('debrid') else ''
		except:
			log_utils.error()
		if 'magnet:' in url:
			if not 'uncached' in item['source']:
				try:
					meta = control.homeWindow.getProperty(self.metaProperty) # need for CM "downlod" action
					if meta:
						meta = jsloads(unquote(meta.replace('%22', '\\"')))
						season = meta.get('season')
						episode = meta.get('episode')
						title = meta.get('title')
					else:
						season = control.homeWindow.getProperty(self.seasonProperty)
						episode = control.homeWindow.getProperty(self.episodeProperty)
						title = control.homeWindow.getProperty(self.titleProperty)
					if debrid_provider == 'Real-Debrid':
						from resources.lib.debrid.realdebrid import RealDebrid as debrid_function
					elif debrid_provider == 'Premiumize.me':
						from resources.lib.debrid.premiumize import Premiumize as debrid_function
					elif debrid_provider == 'AllDebrid':
						from resources.lib.debrid.alldebrid import AllDebrid as debrid_function
					else: return
					url = debrid_function().resolve_magnet(url, item['hash'], season, episode, title)
					self.url = url
					return url
				except:
					log_utils.error()
					return
		else:
			try:
				direct = item['direct']
				call = [i[1] for i in self.sourceDict if i[0] == item['provider']][0]
				if direct:
					url = call.resolve(url)
					self.url = url
					return url
				else:
					if debrid_provider == 'Real-Debrid':
						from resources.lib.debrid.realdebrid import RealDebrid as debrid_function
					elif debrid_provider == 'Premiumize.me':
						from resources.lib.debrid.premiumize import Premiumize as debrid_function
					elif debrid_provider == 'AllDebrid':
						from resources.lib.debrid.alldebrid import AllDebrid as debrid_function
					u = url = call.resolve(url)
					url = debrid_function().unrestrict_link(url)
					self.url = url
					return url
			except:
				log_utils.error()
				return

	def debridPackDialog(self, provider, name, magnet_url, info_hash):
		try:
			if provider in ['Real-Debrid', 'RD']:
				from resources.lib.debrid.realdebrid import RealDebrid as debrid_function
			elif provider in ['Premiumize.me', 'PM']:
				from resources.lib.debrid.premiumize import Premiumize as debrid_function
			elif provider in ['AllDebrid', 'AD']:
				from resources.lib.debrid.alldebrid import AllDebrid as debrid_function
			else: return
			debrid_files = None
			control.busy()
			try: debrid_files = debrid_function().display_magnet_pack(magnet_url, info_hash)
			except: pass
			if not debrid_files:
				control.hide()
				return control.notification(message=32399)
			debrid_files = sorted(debrid_files, key=lambda k: k['filename'].lower())
			display_list = ['%02d | [B]%.2f GB[/B] | [I]%s[/I]' % (count, i['size'], i['filename'].upper()) for count, i in enumerate(debrid_files, 1)]
			control.hide()
			chosen = control.selectDialog(display_list, heading=name)
			if chosen < 0: return None
			if control.condVisibility("Window.IsActive(source_results.xml)"): 	# close "source_results.xml" here after selection is made and valid
				control.closeAll()
			control.busy()
			chosen_result = debrid_files[chosen]
			if provider	 in ['Real-Debrid', 'RD']:
				self.url = debrid_function().unrestrict_link(chosen_result['link'])
			elif provider in ['Premiumize.me', 'PM']:
				self.url = debrid_function().add_headers_to_url(chosen_result['link'])
			elif provider in ['AllDebrid', 'AD']:
				self.url = debrid_function().unrestrict_link(chosen_result['link'])
			from resources.lib.modules import player
			meta = jsloads(unquote(control.homeWindow.getProperty(self.metaProperty).replace('%22', '\\"'))) # needed for CM "showDebridPack" action
			title = meta['tvshowtitle']
			year = meta['year'] if 'year' in meta else None
			season = meta['season'] if 'season' in meta else None
			episode = meta['episode'] if 'episode' in meta else None
			imdb = meta['imdb'] if 'imdb' in meta else None
			tmdb = meta['tmdb'] if 'tmdb' in meta else None
			tvdb = meta['tvdb'] if 'tvdb' in meta else None
			release_title = chosen_result['filename']
			control.hide()
			# if source_utils.seas_ep_filter(season, episode, release_title):
				# return player.Player().play_source(title, year, season, episode, imdb, tmdb, tvdb, self.url, meta)
			# else:
				# return player.Player().play(self.url)
			return player.Player().play(self.url)
		except:
			log_utils.error('Error debridPackDialog: ')
			control.hide()

	def sourceInfo(self, info):
		try:
			supported_platform = any(value in sys_platform for value in ['win32', 'linux2'])
			source = jsloads(info)[0]
			try: f = ' / '.join(['%s' % info.strip() for info in source.get('info').split('|')])
			except: f = ''
			if 'name_info' in source: t = source_utils.getFileType(name_info=source.get('name_info'))
			else: t = source_utils.getFileType(url=source.get('url'))
			t = '%s /%s' % (f, t) if (f != '' and f != '0 ' and f != ' ') else t
			if t == '': t = source_utils.getFileType(url=source.get('url'))
			list = [('[COLOR %s]url:[/COLOR]  %s' % (self.highlight_color, source.get('url')), source.get('url'))]
			# "&" in magnets causes copy2clip to fail
			# if 'magnet:' not in source.get('url') and not source.get('direct'):
				# if supported_platform: list += [('[COLOR %s]  -- Copy url To Clipboard[/COLOR]' % self.highlight_color, ' ')]
			if supported_platform: list += [('[COLOR %s]  -- Copy url To Clipboard[/COLOR]' % self.highlight_color, ' ')]
			list += [('[COLOR %s]name:[/COLOR]  %s' % (self.highlight_color, source.get('name')), source.get('name'))]
			if supported_platform: list += [('[COLOR %s]  -- Copy name To Clipboard[/COLOR]' % self.highlight_color, ' ')]
			list += [('[COLOR %s]info:[/COLOR]  %s' % (self.highlight_color, t), ' ')]
			if 'magnet:' in source.get('url'):
				list += [('[COLOR %s]hash:[/COLOR]  %s' % (self.highlight_color, source.get('hash')), source.get('hash'))]
				if supported_platform: list += [('[COLOR %s]  -- Copy hash To Clipboard[/COLOR]' % self.highlight_color, ' ')]
				list += [('[COLOR %s]seeders:[/COLOR]  %s' % (self.highlight_color, source.get('seeders')), ' ')]
			select = control.selectDialog([i[0] for i in list], 'Source Info')
			if any(x in list[select][0] for x in ['Copy url To Clipboard', 'Copy name To Clipboard', 'Copy hash To Clipboard']):
				source_utils.copy2clip(list[select - 1][1])
			return
		except:
			log_utils.error('Error sourceInfo: ' )

	def alterSources(self, url, meta):
		try:
			if control.setting('play.mode') == '1' or (self.enable_playnext and 'episode' in meta): url += '&select=0'
			else: url += '&select=1'
			control.execute('PlayMedia(%s)' % url)
		except:
			log_utils.error()

	def errorForSources(self):
		try:
			control.sleep(200)
			control.hide()
			if self.url == 'close://': control.notification(message=32400)
			else: control.notification(message=32401)
			control.cancelPlayback()
		except:
			log_utils.error()

	def getAliasTitles(self, imdb, content):
		try:
			t = trakt.getMovieAliases(imdb) if content == 'movie' else trakt.getTVShowAliases(imdb)
			if not t: return []
			t = [i for i in t if i.get('country', '').lower() in ['en', '', 'us', 'uk', 'gb']]
			return t
		except:
			log_utils.error()
			return []

	def getTitle(self, title):
		title = cleantitle.normalize(title)
		return title

	def getConstants(self):
		# self.itemProperty = 'plugin.video.dg.container.items'
		self.metaProperty = 'plugin.video.dg.container.meta'
		self.seasonProperty = 'plugin.video.dg.container.season'
		self.episodeProperty = 'plugin.video.dg.container.episode'
		self.titleProperty = 'plugin.video.dg.container.title'
		self.imdbProperty = 'plugin.video.dg.container.imdb'
		self.tmdbProperty = 'plugin.video.dg.container.tmdb'
		self.tvdbProperty = 'plugin.video.dg.container.tvdb'
		self.labelProperty = 'plugin.video.dg.container.label'

		self.sourceDict = fs_sources()
		self.sourceDict.extend(cloudSources())

		from resources.lib.debrid import premium_hosters
		self.debrid_resolvers = debrid.debrid_resolvers()
		def cache_prDict():
			try:
				hosts = []
				for d in self.debrid_resolvers: hosts += d.get_hosts()[d.name]
				return list(set(hosts))
			except:
				return premium_hosters.hostprDict
		self.hostprDict = providerscache.get(cache_prDict, 192)
		self.sourcecfDict = premium_hosters.sourcecfDict

	def calc_pack_size(self):
		seasoncount = None ; counts = None
		try:
			meta = self.meta
			if meta:
				seasoncount = meta.get('seasoncount', None)
				counts = meta.get('counts', None)
		except:
			log_utils.error()
		if not seasoncount or not counts: # check metacache, 2nd fallback
			try:
				imdb_user = control.setting('imdb.user').replace('ur', '')
				tvdb_key = control.setting('tvdb.api.key')
				user = str(imdb_user) + str(tvdb_key)
				meta_lang = control.apiLanguage()['tvdb']
				if meta:
					imdb = meta.get('imdb', '')
					tmdb = meta.get('tmdb', '')
					tvdb = meta.get('tvdb', '')
				else:
					imdb = control.homeWindow.getProperty(self.imdbProperty)
					tmdb = control.homeWindow.getProperty(self.tmdbProperty)
					tvdb = control.homeWindow.getProperty(self.tvdbProperty)
				ids = [{'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb}]
				meta2 = metacache.fetch(ids, meta_lang, user)[0]
				if not seasoncount: seasoncount = meta2.get('seasoncount', None)
				if not counts: counts = meta2.get('counts', None)
			except:
				log_utils.error()
		if not seasoncount or not counts: # make request, 3rd fallback
			try:
				if meta: season = meta.get('season')
				else: season = control.homeWindow.getProperty(self.seasonProperty)
				from resources.lib.indexers import tmdb as tmdb_indexer
				counts = tmdb_indexer.TVshows().get_counts(tmdb)
				seasoncount = counts[str(season)]
			except:
				log_utils.error()
				return self.sources
		for i in self.sources:
			try:
				if 'package' in i:
					dsize = i.get('size')
					if not dsize: continue
					if i['package'] == 'season':
						divider = int(seasoncount)
						if not divider: continue
					else:
						if not counts: continue
						season_count = 1 ; divider = 0
						while season_count <= int(i['last_season']):
							divider += int(counts[str(season_count)])
							season_count += 1
					float_size = float(dsize) / divider
					if round(float_size, 2) == 0: continue
					str_size = '%.2f GB' % float_size
					info = i['info']
					try: info = [i['info'].split(' | ', 1)[1]]
					except: info = []
					info.insert(0, str_size)
					info = ' | '.join(info)
					i.update({'size': float_size, 'info': info})
				else:
					continue
			except:
				log_utils.error()
				continue
		return self.sources

	def ad_cache_chk_list(self, torrent_List):
		if len(torrent_List) == 0: return
		try:
			hashList = [i['hash'] for i in torrent_List]
			cached = alldebrid.AllDebrid().check_cache(hashList)
			if not cached: return None
			cached = cached['magnets']
			count = 0
			for i in torrent_List:
				if 'error' in cached[count]:
					count += 1
					continue
				if cached[count]['instant'] is False:
					if 'package' in i: i.update({'source': 'uncached (pack) torrent'})
					else: i.update({'source': 'uncached torrent'})
				else:
					if 'package' in i: i.update({'source': 'cached (pack) torrent'})
					else: i.update({'source': 'cached torrent'})
				count += 1
			return torrent_List
		except:
			log_utils.error()

	def pm_cache_chk_list(self, torrent_List):
		if len(torrent_List) == 0: return
		try:
			hashList = [i['hash'] for i in torrent_List]
			cached = premiumize.Premiumize().check_cache_list(hashList)
			if not cached: return None
			count = 0
			for i in torrent_List:
				if cached[count] is False:
					if 'package' in i: i.update({'source': 'uncached (pack) torrent'})
					else: i.update({'source': 'uncached torrent'})
				else:
					if 'package' in i: i.update({'source': 'cached (pack) torrent'})
					else: i.update({'source': 'cached torrent'})
				count += 1
			return torrent_List
		except:
			log_utils.error()

	def rd_cache_chk_list(self, torrent_List):
		if len(torrent_List) == 0: return
		def base32_to_hex(hash):
			from base64 import b32decode
			log_utils.log('RD base32 hash: %s' % hash, __name__, log_utils.LOGDEBUG)
			hex = b32decode(hash).hex()
			log_utils.log('RD base32_to_hex: %s' % hex, __name__, log_utils.LOGDEBUG)
			return hex
		try:
			hashList = [i['hash'] if len(i['hash']) == 40 else base32_to_hex(i['hash']) for i in torrent_List] # RD can not handle BASE32 encoded hashes, hex 40 only (AD and PM convert)
			cached = realdebrid.RealDebrid().check_cache_list(hashList)
			if not cached: return None
			for i in torrent_List:
				if 'rd' not in cached.get(i['hash'].lower(), {}):
					if 'package' in i: i.update({'source': 'uncached (pack) torrent'})
					else: i.update({'source': 'uncached torrent'})
					continue
				elif len(cached[i['hash'].lower()]['rd']) >= 1:
					if 'package' in i: i.update({'source': 'cached (pack) torrent'})
					else: i.update({'source': 'cached torrent'})
				else:
					if 'package' in i: i.update({'source': 'uncached (pack) torrent'})
					else: i.update({'source': 'uncached torrent'})
			return torrent_List
		except:
			log_utils.error()

	def clr_item_providers(self, title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered):
		providerscache.remove(self.getSources, title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered) # function cache removal of selected item ONLY
		try:
			dbcon = database.connect(self.sourceFile)
			dbcur = dbcon.cursor()
			dbcur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='rel_src';''') # table exists so both all will
			if dbcur.fetchone()[0] == 1:
				dbcur.execute('''DELETE FROM rel_src WHERE imdb_id=?''', (imdb,)) # DEL the "rel_src" list of cached links
				if not tvshowtitle:
					dbcur.execute('''DELETE FROM rel_url WHERE imdb_id=?''', (imdb,)) #only DEL movies "rel_url" so imdb year check may update for setting change
				dbcur.connection.commit()
		except:
			log_utils.error()
		finally:
			dbcur.close() ; dbcon.close()

	def movie_chk_imdb(self, imdb, title, year):
		try:
			if not imdb or imdb == '0': return year, title
			from resources.lib.modules.client import _basic_request
			result = _basic_request('https://v2.sg.media-imdb.com/suggestion/t/{}.json'.format(imdb))
			if not result: return year, title
			result = jsloads(result)['d'][0]
			year_ck = str(result['y'])
			title_ck = self.getTitle(result['l'])
			if not year_ck or not title_ck: return year, title
			if year != year_ck:
				log_utils.log('IMDb year_ck: (%s) does not match meta year passed: (%s) for title: (%s)' % (year_ck, year, title), __name__, level=log_utils.LOGDEBUG)
				year = year_ck
			if title != title_ck:
				log_utils.log('IMDb title_ck: (%s) does not match meta tile passed: (%s)' % (title_ck, title), __name__, level=log_utils.LOGDEBUG)
				title = title_ck
			return year, title
		except:
			log_utils.error()
			return year, title

	def get_season_info(self, imdb, tmdb, tvdb, meta, season):
		total_seasons = None
		season_isAiring = None
		try:
			total_seasons = meta.get('total_seasons', None)
			season_isAiring = meta.get('season_isAiring', None)
		except: pass
		if not total_seasons or season_isAiring is None: # check metacache, 2nd fallback
			try:
				imdb_user = control.setting('imdb.user').replace('ur', '')
				tvdb_key = control.setting('tvdb.api.key')
				user = str(imdb_user) + str(tvdb_key)
				meta_lang = control.apiLanguage()['tvdb']
				ids = [{'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb}]
				meta2 = metacache.fetch(ids, meta_lang, user)[0]
				if not total_seasons: total_seasons = meta2.get('total_seasons', None)
				if season_isAiring is None: season_isAiring = meta2.get('season_isAiring', None)
			except:
				log_utils.error()
		if not total_seasons: # make request, 3rd fallback
			try:
				total_seasons = trakt.getSeasons(imdb, full=False)
				if total_seasons:
					total_seasons = [i['number'] for i in total_seasons]
					season_special = True if 0 in total_seasons else False
					total_seasons = len(total_seasons)
					if season_special: total_seasons = total_seasons - 1
			except:
				log_utils.error()
		if season_isAiring is None:
			try:
				from resources.lib.indexers import tmdb as tmdb_indexer
				season_isAiring = tmdb_indexer.TVshows().get_season_isAiring(tmdb, season)
				if not season_isAiring: season_isAiring = 'false'
			except:
				log_utils.error()
		return total_seasons, season_isAiring

	def debrid_abv(self, debrid):
		try:
			d_dict = {'AllDebrid': 'AD', 'Premiumize.me': 'PM', 'Real-Debrid': 'RD'}
			d = d_dict[debrid]
		except:
			log_utils.error()
			d = ''
		return d
