# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from hashlib import md5
from json import dumps as jsdumps, loads as jsloads
from sys import argv, exit as sysexit
try: from sqlite3 import dbapi2 as database
except ImportError: from pysqlite2 import dbapi2 as database
import xbmc
from resources.lib.database import metacache
from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import playcount
from resources.lib.modules import trakt

LOGINFO = 1
homeWindow = control.homeWindow
playerWindow = control.playerWindow


class Player(xbmc.Player):
	def __init__(self):
		xbmc.Player.__init__(self)
		self.play_next_triggered = False
		self.preScrape_triggered = False
		self.playbackStopped_triggered = False
		self.playback_resumed = False
		self.onPlayBackStarted_called = False
		self.onPlayBackStopped_ran = False
		self.media_type = None
		self.DBID = None
		self.offset = '0'
		self.media_length = 0
		self.current_time = 0
		self.meta = {}
		self.enable_playnext = control.setting('enable.playnext') == 'true'
		self.playnext_time = int(control.setting('playnext.time')) or 60
		self.traktCredentials = trakt.getTraktCredentialsInfo()

	def play_source(self, title, year, season, episode, imdb, tmdb, tvdb, url, meta, debridPackCall=False):
		try:
			from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
			if not url: raise Exception
			self.media_type = 'movie' if season is None or episode is None else 'episode'
			self.title, self.year = title, str(year)
			if self.media_type == 'movie':
				self.name, self.season, self.episode = '%s (%s)' % (title, self.year), None, None
			elif self.media_type == 'episode':
				self.name, self.season, self.episode = '%s S%02dE%02d' % (title, int(season), int(episode)), '%01d' % int(season), '%01d' % int(episode)
			self.imdb, self.tmdb, self.tvdb = imdb or '', tmdb or '', tvdb or ''
			self.ids = {'imdb': self.imdb, 'tmdb': self.tmdb, 'tvdb': self.tvdb}
## - compare meta received to database and use largest(eventually switch to a request to fetch missing db meta for item)
			self.imdb_user = control.setting('imdb.user').replace('ur', '')
			self.tmdb_key = control.setting('tmdb.api.key')
			if not self.tmdb_key: self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
			self.tvdb_key = control.setting('tvdb.api.key')
			if self.media_type == 'episode': self.user = str(self.imdb_user) + str(self.tvdb_key)
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
			poster, thumb, season_poster, fanart, banner, clearart, clearlogo, discart, meta = self.getMeta(meta)
			self.offset = Bookmarks().get(name=self.name, imdb=imdb, tmdb=tmdb, tvdb=tvdb, season=season, episode=episode, year=self.year, runtime=meta.get('duration') if meta else 0)

			if self.offset == '-1':
				log_utils.log('User requested playback cancel', level=log_utils.LOGDEBUG)
				control.notification(message=32328)
				return control.cancelPlayback()

			item = control.item(path=url)
			item.setUniqueIDs(self.ids)
			if self.media_type == 'episode':
				item.setArt({'tvshow.clearart': clearart, 'tvshow.clearlogo': clearlogo, 'tvshow.discart': discart, 'thumb': thumb, 'tvshow.poster': season_poster, 'season.poster': season_poster, 'tvshow.fanart': fanart})
			else:
				item.setArt({'clearart': clearart, 'clearlogo': clearlogo, 'discart': discart, 'thumb': thumb, 'poster': poster, 'fanart': fanart})
			if 'castandart' in meta: item.setCast(meta.get('castandart', ''))
			item.setInfo(type='video', infoLabels=control.metadataClean(meta))
			item.setProperty('IsPlayable', 'true')
			if debridPackCall: control.player.play(url, item) # seems this is only way browseDebrid pack files will play and have meta marked as watched
			else: control.resolve(int(argv[1]), True, item)
			homeWindow.setProperty('script.trakt.ids', jsdumps(self.ids))
			self.keepAlive()
			homeWindow.clearProperty('script.trakt.ids')
		except:
			log_utils.error()
			return control.cancelPlayback()

	def getMeta(self, meta):
		try:
			if not meta or ('videodb' in control.infoLabel('ListItem.FolderPath')): raise Exception()
			poster = meta.get('poster3') or meta.get('poster2') or meta.get('poster') #poster2 and poster3 may not be passed anymore
			thumb = meta.get('thumb')
			thumb = thumb or poster or control.addonThumb()
			season_poster = meta.get('season_poster') or poster
			fanart = meta.get('fanart')
			banner = meta.get('banner')
			clearart = meta.get('clearart')
			clearlogo = meta.get('clearlogo')
			discart = meta.get('discart')
			if 'mediatype' not in meta:
				meta.update({'mediatype': 'episode' if self.episode else 'movie'})
				if self.episode: meta.update({'tvshowtitle': self.title, 'season': self.season, 'episode': self.episode})
			return (poster, thumb, season_poster, fanart, banner, clearart, clearlogo, discart, meta)
		except:
			log_utils.error()
		try:
			def cleanLibArt(art):
				from urllib.parse import unquote
				if not art: return ''
				art = unquote(art.replace('image://', ''))
				if art.endswith('/'): art = art[:-1]
				return art
			def sourcesDirMeta(metadata): # pass player minimal meta needed from lib pull
				if not metadata: return metadata
				allowed = ['mediatype', 'imdb', 'tmdb', 'tvdb', 'poster', 'season_poster', 'fanart', 'banner', 'clearart', 'clearlogo', 'discart', 'thumb', 'title', 'tvshowtitle', 'year', 'premiered', 'rating', 'plot', 'duration', 'mpaa', 'season', 'episode', 'castandrole']
				return {k: v for k, v in iter(metadata.items()) if k in allowed}
			poster, thumb, season_poster, fanart, banner, clearart, clearlogo, discart, meta = '', '', '', '', '', '', '', '', {'title': self.name}
			if self.media_type != 'movie': raise Exception()
			# do not add IMDBNUMBER as tmdb scraper puts their id in the key value
			meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "uniqueid", "year", "premiered", "genre", "studio", "country", "runtime", "rating", "votes", "mpaa", "director", "writer", "cast", "plot", "plotoutline", "tagline", "thumbnail", "art", "file"]}, "id": 1}' % (self.year, str(int(self.year) + 1), str(int(self.year) - 1)))
			meta = jsloads(meta)['result']['movies']
			meta = [i for i in meta if (i.get('uniqueid', []).get('imdb', '') == self.imdb) or (i.get('uniqueid', []).get('unknown', '') == self.imdb)] # scraper now using "unknown"
			if meta: meta = meta[0]
			else: raise Exception()
			if 'mediatype' not in meta: meta.update({'mediatype': 'movie'})
			if 'duration' not in meta: meta.update({'duration': meta.get('runtime')}) # Trakt scrobble resume needs this for lib playback
			if 'castandrole' not in meta: meta.update({'castandrole': [(i['name'], i['role']) for i in meta.get('cast')]})
			thumb = cleanLibArt(meta.get('art').get('thumb', ''))
			poster = cleanLibArt(meta.get('art').get('poster', '')) or self.poster
			fanart = cleanLibArt(meta.get('art').get('fanart', '')) or self.fanart
			banner = cleanLibArt(meta.get('art').get('banner', '')) # not sure this is even used by player
			clearart = cleanLibArt(meta.get('art').get('clearart', ''))
			clearlogo = cleanLibArt(meta.get('art').get('clearlogo', ''))
			discart = cleanLibArt(meta.get('art').get('discart'))
			if 'plugin' not in control.infoLabel('Container.PluginName'):
				self.DBID = meta.get('movieid')
			meta = sourcesDirMeta(meta)
			return (poster, thumb, '', fanart, banner, clearart, clearlogo, discart, meta)
		except:
			log_utils.error()
		try:
			if self.media_type != 'episode': raise Exception()
			# do not add IMDBNUMBER as tmdb scraper puts their id in the key value
			show_meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "uniqueid", "mpaa", "year", "genre", "runtime", "thumbnail", "file"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
			show_meta = jsloads(show_meta)['result']['tvshows']
			show_meta = [i for i in show_meta if i['uniqueid']['imdb'] == self.imdb]
			show_meta = [i for i in show_meta if (i.get('uniqueid', []).get('imdb', '') == self.imdb) or (i.get('uniqueid', []).get('unknown', '') == self.imdb)] # scraper now using "unknown"
			if show_meta: show_meta = show_meta[0]
			else: raise Exception()
			tvshowid = show_meta['tvshowid']
			meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params":{"tvshowid": %d, "filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["showtitle", "title", "season", "episode", "firstaired", "runtime", "rating", "director", "writer", "cast", "plot", "thumbnail", "art", "file"]}, "id": 1}' % (tvshowid, self.season, self.episode))
			meta = jsloads(meta)['result']['episodes']
			if meta: meta = meta[0]
			else: raise Exception()
			if 'mediatype' not in meta: meta.update({'mediatype': 'episode'})
			if 'tvshowtitle' not in meta: meta.update({'tvshowtitle': meta.get('showtitle')})
			if 'castandrole' not in meta: meta.update({'castandrole': [(i['name'], i['role']) for i in meta.get('cast')]})
			if 'genre' not in meta: meta.update({'genre': show_meta.get('genre')})
			if 'duration' not in meta: meta.update({'duration': meta.get('runtime')}) # Trakt scrobble resume needs this for lib playback but Kodi lib returns "0" for shows or episodes
			if 'mpaa' not in meta: meta.update({'mpaa': show_meta.get('mpaa')})
			if 'premiered' not in meta: meta.update({'premiered': meta.get('firstaired')})
			if 'year' not in meta: meta.update({'year': show_meta.get('year')}) # shows year not year episode aired
			thumb = cleanLibArt(meta.get('art').get('thumb', ''))
			season_poster = poster = cleanLibArt(meta.get('art').get('season.poster', '')) or self.poster
			fanart = cleanLibArt(meta.get('art').get('tvshow.fanart', '')) or self.poster
			banner = cleanLibArt(meta.get('art').get('tvshow.banner', '')) # not sure this is even used by player
			clearart = cleanLibArt(meta.get('art').get('tvshow.clearart', ''))
			clearlogo = cleanLibArt(meta.get('art').get('tvshow.clearlogo', ''))
			discart = cleanLibArt(meta.get('art').get('discart'))
			if 'plugin' not in control.infoLabel('Container.PluginName'):
				self.DBID = meta.get('episodeid')
			meta = sourcesDirMeta(meta)
			return (poster, thumb, season_poster, fanart, banner, clearart, clearlogo, discart, meta)
		except:
			log_utils.error()
			return (poster, thumb, season_poster, fanart, banner, clearart, clearlogo, discart, meta)

	def getWatchedPercent(self):
		if self.isPlayback():
			try:
				position = self.getTime()
				if position != 0: self.current_time = position
				total_length = self.getTotalTime()
				if total_length != 0: self.media_length = total_length
			except: pass
		current_position = self.current_time
		total_length = self.media_length
		watched_percent = 0
		if int(total_length) != 0:
			try:
				watched_percent = float(current_position) / float(total_length) * 100
				if watched_percent > 100: watched_percent = 100
			except:
				log_utils.error()
		return watched_percent

	def getRemainingTime(self):
		remaining_time = 0
		if self.isPlayback():
			try:
				current_position = self.getTime()
				remaining_time = int(self.media_length) - int(current_position)
			except: pass
		return remaining_time

	def keepAlive(self):
		pname = '%s.player.overlay' % control.addonInfo('id')
		homeWindow.clearProperty(pname)
		for i in range(0, 500):
			if self.isPlayback():
				control.closeAll()
				break
			xbmc.sleep(200)
		while self.isPlayingVideo():
			try:
				if control.monitor.abortRequested(): return sysexit()
				try:
					self.current_time = self.getTime()
					self.media_length = self.getTotalTime()
				except: pass
				watcher = (self.getWatchedPercent() >= 85)
				property = homeWindow.getProperty(pname)
				if self.media_type == 'movie':
					try:
						if watcher and property != '5':
							homeWindow.setProperty(pname, '5')
							playcount.markMovieDuringPlayback(self.imdb, '5')
					except: pass
					xbmc.sleep(2000)
				elif self.media_type == 'episode':
					try:
						if watcher and property != '5':
							homeWindow.setProperty(pname, '5')
							playcount.markEpisodeDuringPlayback(self.imdb, self.tvdb, self.season, self.episode, '5')
						if self.enable_playnext and not self.play_next_triggered:
							if int(control.playlist.size()) > 1:
								if self.preScrape_triggered == False:
									xbmc.executebuiltin('RunPlugin(plugin://plugin.video.dg/?action=play_preScrapeNext)')
									self.preScrape_triggered = True
								remaining_time = self.getRemainingTime()
								if remaining_time < (self.playnext_time + 1) and remaining_time != 0:
									xbmc.executebuiltin('RunPlugin(plugin://plugin.video.dg/?action=play_nextWindowXML)')
									self.play_next_triggered = True
					except:
						log_utils.error()
						pass
					xbmc.sleep(1000)
			except:
				log_utils.error()
				xbmc.sleep(1000)
		homeWindow.clearProperty(pname)
		# self.onPlayBackEnded() # check, kodi may at times not issue "onPlayBackEnded" callback
		if self.media_length - self.current_time > 60: # kodi may at times not issue "onPlayBackStopped" callback
			self.playbackStopped_triggered = True
			self.onPlayBackStopped()

	def libForPlayback(self):
		if self.DBID is None: return
		try:
			if self.media_type == 'movie':
				rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid": %s, "playcount": 1 }, "id": 1 }' % str(self.DBID)
			elif self.media_type == 'episode':
				rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid": %s, "playcount": 1 }, "id": 1 }' % str(self.DBID)
			control.jsonrpc(rpc)
		except:
			log_utils.error()

	def isPlayback(self):
		# Kodi often starts playback where isPlaying() is true and isPlayingVideo() is false, since the video loading is still in progress, whereas the play is already started.
		return self.isPlaying() and self.isPlayingVideo() and self.getTime() >= 0

	def onPlayBackSeek(self, time, seekOffset):
		seekOffset /= 1000

	def onAVStarted(self):
		if self.onPlayBackStarted_called:
			xbmc.log('[ plugin.video.dg ] onAVStarted callback, onPlayBackStarted already called', LOGINFO)
			return log_utils.log('[ plugin.video.dg ] onAVStarted callback, onPlayBackStarted already called', level=log_utils.LOGDEBUG)
		self.onPlayBackStarted()

	def onPlayBackStarted(self): # gets called before onAVStarted()
		self.onPlayBackStarted_called = True
		for i in range(0, 500):
			if self.isPlayback():
				control.closeAll()
				break
			else: control.sleep(200)
		if self.offset != '0' and self.playback_resumed is False:
			control.sleep(200)
			self.seekTime(float(self.offset))
			self.playback_resumed = True
		if control.setting('subtitles') == 'true':
			Subtitles().get(self.name, self.imdb, self.season, self.episode)
		xbmc.log('[ plugin.video.dg ] onPlayBackStarted callback', LOGINFO)
		log_utils.log('[ plugin.video.dg ] onPlayBackStarted callback', level=log_utils.LOGDEBUG)

	def onPlayBackStopped(self):
		try:
			playerWindow.clearProperty('dg.preResolved_nextUrl')
			if not self.onPlayBackStopped_ran or (self.playbackStopped_triggered and not self.onPlayBackStopped_ran): # Kodi callback unreliable and often not issued
				self.onPlayBackStopped_ran = True
				self.playbackStopped_triggered = False
				Bookmarks().reset(self.current_time, self.media_length, self.name, self.year)
				if self.traktCredentials and (control.setting('trakt.scrobble') == 'true'):
					Bookmarks().set_scrobble(self.current_time, self.media_length, self.media_type, self.imdb, self.tmdb, self.tvdb, self.season, self.episode)
				watcher = self.getWatchedPercent()
				seekable = (int(self.current_time) > 180 and (watcher < 85))
				if watcher >= 85: self.libForPlayback() # only write playcount to local lib
				if control.setting('crefresh') == 'true' and seekable: control.refresh() #not all skins refresh after playback stopped
				control.playlist.clear()
				# control.trigger_widget_refresh() # skinshortcuts handles widget refresh
				xbmc.log('[ plugin.video.dg ] onPlayBackStopped callback', LOGINFO)
				log_utils.log('[ plugin.video.dg ] onPlayBackStopped callback', level=log_utils.LOGDEBUG)
		except:
			log_utils.error()

	def onPlayBackEnded(self):
		Bookmarks().reset(self.current_time, self.media_length, self.name, self.year)
		if self.traktCredentials:
			trakt.scrobbleReset(imdb=self.imdb, tvdb=self.tvdb, season=self.season, episode=self.episode, refresh=False) # refresh issues container.refresh()
		self.libForPlayback()
		if control.playlist.getposition() == control.playlist.size() or control.playlist.size() == 1:
			control.playlist.clear()
		xbmc.log('[ plugin.video.dg ] onPlayBackEnded callback', LOGINFO)
		log_utils.log('[ plugin.video.dg ] onPlayBackEnded callback', level=log_utils.LOGDEBUG)

	def onPlayBackError(self):
		playerWindow.clearProperty('dg.preResolved_nextUrl')
		Bookmarks().reset(self.current_time, self.media_length, self.name, self.year)
		log_utils.error()
		xbmc.log('[ plugin.video.dg ] onPlayBackError callback', LOGINFO)
		log_utils.log('[ plugin.video.dg ] onPlayBackError callback', level=log_utils.LOGDEBUG)
		sysexit(1)


class PlayNext(xbmc.Player):
	def __init__(self):
		super(PlayNext, self).__init__()
		self.enable_playnext = control.setting('enable.playnext') == 'true'
		self.stillwatching_count = int(control.setting('stillwatching.count'))
		self.playing_file = None

	def display_xml(self):
		try:
			self.playing_file = self.getPlayingFile()
		except:
			log_utils.error("Kodi did not return a playing file, killing playnext xml's")
			return
		if control.playlist.size() > 0 and control.playlist.getposition() != (control.playlist.size() - 1):
			if self.isStill_watching(): target = self.show_stillwatching_xml
			elif self.enable_playnext: target = self.show_playnext_xml
			else: return
			if self.playing_file != self.getPlayingFile(): return
			if not self.isPlayingVideo(): return
			if control.getCurrentWindowId != 12005: return
			target()

	def isStill_watching(self):
		still_watching = float(control.playlist.getposition() + 1) / self.stillwatching_count
		if still_watching == 0: return False
		return still_watching.is_integer()

	def getNext_meta(self):
		try:
			from urllib.parse import parse_qsl
			current_position = control.playlist.getposition()
			next_url = control.playlist[current_position + 1].getPath()
			# next_url=videodb://tvshows/titles/16/2/571?season=2&tvshowid=16 # library playback returns this
			params = dict(parse_qsl(next_url.replace('?', '')))
			next_meta = jsloads(params.get('meta')) if params.get('meta') else '' # not available for library playback
			return next_meta
		except:
			log_utils.error()
			return ''

	def show_playnext_xml(self):
		try:
			next_meta = self.getNext_meta()
			if not next_meta: raise Exception()
			from resources.lib.windows.playnext import PlayNextXML
			window = PlayNextXML('playnext.xml', control.addonPath(control.addonId()), meta=next_meta)
			window.run()
			del window
			self.play_next_triggered = True
		except:
			log_utils.error()
			self.play_next_triggered = True

	def show_stillwatching_xml(self):
		try:
			next_meta = self.getNext_meta()
			if not next_meta: raise Exception()
			from resources.lib.windows.playnext_stillwatching import StillWatchingXML
			window = StillWatchingXML('playnext_stillwatching.xml', control.addonPath(control.addonId()), meta=next_meta)
			window.run()
			del window
			self.play_next_triggered = True
		except:
			log_utils.error()
			self.play_next_triggered = True

	def prescrapeNext(self):
		try:
			if control.playlist.size() > 0 and control.playlist.getposition() != (control.playlist.size() - 1):
				from resources.lib.modules import sources
				from resources.lib.database import providerscache
				next_meta=self.getNext_meta()
				if not next_meta: raise Exception()
				title = next_meta.get('title')
				year = next_meta.get('year')
				imdb = next_meta.get('imdb')
				tmdb = next_meta.get('tmdb')
				tvdb = next_meta.get('tvdb')
				season = next_meta.get('season')
				episode = next_meta.get('episode')
				tvshowtitle = next_meta.get('tvshowtitle')
				premiered = next_meta.get('premiered')
				next_sources = providerscache.get(sources.Sources().getSources, 48, title, year, imdb, tmdb, tvdb, str(season), str(episode), tvshowtitle, premiered, next_meta, True)
				if not self.isPlayingVideo():
					return playerWindow.clearProperty('dg.preResolved_nextUrl')


				sources.Sources().preResolve(next_sources, next_meta)
			else:
				playerWindow.clearProperty('dg.preResolved_nextUrl')
		except:
			log_utils.error()
			playerWindow.clearProperty('dg.preResolved_nextUrl')


class Subtitles:
	def get(self, name, imdb, season, episode):
		try:
			import gzip, codecs
			from io import BytesIO
			import re, base64
			import xmlrpc.client as xmlrpc_client
		except:
			log_utils.error()
			return
		try:
			langDict = {'Afrikaans': 'afr', 'Albanian': 'alb', 'Arabic': 'ara', 'Armenian': 'arm', 'Basque': 'baq', 'Bengali': 'ben',
			'Bosnian': 'bos', 'Breton': 'bre', 'Bulgarian': 'bul', 'Burmese': 'bur', 'Catalan': 'cat', 'Chinese': 'chi', 'Croatian': 'hrv',
			'Czech': 'cze', 'Danish': 'dan', 'Dutch': 'dut', 'English': 'eng', 'Esperanto': 'epo', 'Estonian': 'est', 'Finnish': 'fin',
			'French': 'fre', 'Galician': 'glg', 'Georgian': 'geo', 'German': 'ger', 'Greek': 'ell', 'Hebrew': 'heb', 'Hindi': 'hin',
			'Hungarian': 'hun', 'Icelandic': 'ice', 'Indonesian': 'ind', 'Italian': 'ita', 'Japanese': 'jpn', 'Kazakh': 'kaz', 'Khmer': 'khm',
			'Korean': 'kor', 'Latvian': 'lav', 'Lithuanian': 'lit', 'Luxembourgish': 'ltz', 'Macedonian': 'mac', 'Malay': 'may',
			'Malayalam': 'mal', 'Manipuri': 'mni', 'Mongolian': 'mon', 'Montenegrin': 'mne', 'Norwegian': 'nor', 'Occitan': 'oci',
			'Persian': 'per', 'Polish': 'pol', 'Portuguese': 'por,pob', 'Portuguese(Brazil)': 'pob,por', 'Romanian': 'rum', 'Russian': 'rus',
			'Serbian': 'scc', 'Sinhalese': 'sin', 'Slovak': 'slo', 'Slovenian': 'slv', 'Spanish': 'spa', 'Swahili': 'swa', 'Swedish': 'swe',
			'Syriac': 'syr', 'Tagalog': 'tgl', 'Tamil': 'tam', 'Telugu': 'tel', 'Thai': 'tha', 'Turkish': 'tur', 'Ukrainian': 'ukr', 'Urdu': 'urd'}
			codePageDict = {'ara': 'cp1256', 'ar': 'cp1256', 'ell': 'cp1253', 'el': 'cp1253', 'heb': 'cp1255',
									'he': 'cp1255', 'tur': 'cp1254', 'tr': 'cp1254', 'rus': 'cp1251', 'ru': 'cp1251'}
			quality = ['bluray', 'hdrip', 'brrip', 'bdrip', 'dvdrip', 'webrip', 'hdtv']
			langs = []
			try:
				try: langs = langDict[control.setting('subtitles.lang.1')].split(',')
				except: langs.append(langDict[control.setting('subtitles.lang.1')])
			except: pass
			try:
				try: langs = langs + langDict[control.setting('subtitles.lang.2')].split(',')
				except: langs.append(langDict[control.setting('subtitles.lang.2')])
			except: pass
			try: subLang = xbmc.Player().getSubtitles()
			except: subLang = ''

			if subLang == langs[0]: raise Exception()
			server = xmlrpc_client.Server('https://api.opensubtitles.org/xml-rpc', verbose=0)
			# token = server.LogIn('', '', 'en', 'XBMC_Subtitles_v1')
			token = server.LogIn('', '', 'en', 'XBMC_Subtitles_Unofficial_v5.2.14') # service.subtitles.opensubtitles_by_opensubtitles
			if 'token' not in token:
				return log_utils.log('OpenSubtitles Login failed: token=%s' % token, level=log_utils.LOGWARNING)
			else: token = token['token']

			sublanguageid = ','.join(langs)
			imdbid = re.sub(r'[^0-9]', '', imdb)
			if not (season is None or episode is None):
				result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid, 'season': season, 'episode': episode}])['data']
				fmt = ['hdtv']
			else:
				result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid}])['data']
				try: vidPath = xbmc.Player().getPlayingFile()
				except: vidPath = ''
				fmt = re.split(r'\.|\(|\)|\[|\]|\s|\-', vidPath)
				fmt = [i.lower() for i in fmt]
				fmt = [i for i in fmt if i in quality]
			filter = []
			result = [i for i in result if i['SubSumCD'] == '1']
			for lang in langs:
				filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in fmt)]
				filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in quality)]
				filter += [i for i in result if i['SubLanguageID'] == lang]

			try: lang = xbmc.convertLanguage(filter[0]['SubLanguageID'], xbmc.ISO_639_1)
			except: lang = filter[0]['SubLanguageID']
			filename = filter[0]['SubFileName']
			log_utils.log('downloaded subtitle=%s' % filename, level=log_utils.LOGDEBUG)

			content = [filter[0]['IDSubtitleFile'],]
			content = server.DownloadSubtitles(token, content)
			content = base64.b64decode(content['data'][0]['data'])
			content = gzip.GzipFile(fileobj=BytesIO(content)).read()
			subtitle = control.transPath('special://temp/')
			subtitle = control.joinPath(subtitle, 'TemporarySubs.%s.srt' % lang)
			log_utils.log('subtitle file = %s' % subtitle, level=log_utils.LOGDEBUG)

			codepage = codePageDict.get(lang, '')
			if codepage and control.setting('subtitles.utf') == 'true':
				try:
					content_encoded = codecs.decode(content, codepage) # check for kodi 19?
					content = codecs.encode(content_encoded, 'utf-8') # check for kodi 19?
				except: pass

			file = control.openFile(subtitle, 'w')
			file.write(content)
			file.close()
			xbmc.sleep(1000)
			xbmc.Player().setSubtitles(subtitle)
			if control.setting('subtitles.notification') == 'true':
				if Player().isPlayback():
					control.sleep(500)
					control.notification(title=filename, message=control.lang(32191) % lang.upper())
		except:
			log_utils.error()


class Bookmarks:
	def get(self, name, imdb=None, tmdb=None, tvdb=None, season=None, episode=None, year='0', runtime=None, ck=False):
		offset = '0'
		scrobbble = 'Local Bookmark'
		if control.setting('bookmarks') != 'true': return offset
		if control.setting('trakt.scrobble') == 'true' and control.setting('resume.source') == '1':
			scrobbble = 'Trakt Scrobble'
			try:
				if not runtime or runtime == 'None': return offset # TMDB sometimes return None as string. duration pulled from kodi library if missing from meta
				from resources.lib.database import traktsync
				progress = float(traktsync.fetch_bookmarks(imdb, tmdb, tvdb, season, episode))
				offset = float(progress / 100) * int(float(runtime)) # runtime vs. media_length can differ resulting in 10-30sec difference using Trakt scrobble, meta providers report runtime in full minutes
				seekable = (2 <= progress <= 85)
				if not seekable: return '0'
			except:
				log_utils.error()
				return '0'
		else:
			try:
				dbcon = database.connect(control.bookmarksFile)
				dbcur = dbcon.cursor()
				dbcur.execute('''CREATE TABLE IF NOT EXISTS bookmark (idFile TEXT, timeInSeconds TEXT, Name TEXT, year TEXT, UNIQUE(idFile));''')
				if not year or year == 'None': return offset
				years = [str(year), str(int(year)+1), str(int(year)-1)]
				match = dbcur.execute('''SELECT * FROM bookmark WHERE Name="%s" AND year IN (%s)''' % (name, ','.join(i for i in years))).fetchone() # helps fix random cases where trakt and imdb, or tvdb, differ by a year for eps
			except:
				log_utils.error()
				return offset
			finally:
				dbcur.close() ; dbcon.close()
			if not match: return offset
			offset = str(match[1])
		if ck: return offset
		minutes, seconds = divmod(float(offset), 60)
		hours, minutes = divmod(minutes, 60)
		label = '%02d:%02d:%02d' % (hours, minutes, seconds)
		label = control.lang(32502) % label
		if control.setting('bookmarks.auto') == 'false':
			select = control.yesnocustomDialog(label, scrobbble, '', str(name), 'Cancel Playback', control.lang(32503), control.lang(32501))
			if select == 1: offset = '0'
			elif select == -1 or select == 2: offset = '-1'
		return offset

	def reset(self, current_time, media_length, name, year='0'):
		try:
			from resources.lib.database import cache
			cache.clear_local_bookmarks()
			if control.setting('bookmarks') != 'true' or media_length == 0 or current_time == 0: return
			timeInSeconds = str(current_time)
			seekable = (int(current_time) > 180 and (current_time / media_length) < .85)
			idFile = md5()
			try: [idFile.update(str(i)) for i in name]
			except: [idFile.update(str(i).encode('utf-8')) for i in name]
			try: [idFile.update(str(i)) for i in year]
			except: [idFile.update(str(i).encode('utf-8')) for i in year]
			idFile = str(idFile.hexdigest())
			control.makeFile(control.dataPath)
			dbcon = database.connect(control.bookmarksFile)
			dbcur = dbcon.cursor()
			dbcur.execute('''CREATE TABLE IF NOT EXISTS bookmark (idFile TEXT, timeInSeconds TEXT, Name TEXT, year TEXT, UNIQUE(idFile));''')
			years = [str(year), str(int(year) + 1), str(int(year) - 1)]
			dbcur.execute('''DELETE FROM bookmark WHERE Name="%s" AND year IN (%s)''' % (name, ','.join(i for i in years))) #helps fix random cases where trakt and imdb, or tvdb, differ by a year for eps
			if seekable:
				dbcur.execute('''INSERT INTO bookmark Values (?, ?, ?, ?)''', (idFile, timeInSeconds, name, year))
				minutes, seconds = divmod(float(timeInSeconds), 60)
				hours, minutes = divmod(minutes, 60)
				label = ('%02d:%02d:%02d' % (hours, minutes, seconds))
				message = control.lang(32660)
				control.notification(title=name, message=message + '(' + label + ')')
			dbcur.connection.commit()
			try: dbcur.close ; dbcon.close()
			except: pass
		except:
			log_utils.error()

	def set_scrobble(self, current_time, media_length, media_type, imdb='', tmdb='', tvdb='', season='', episode=''):
		try:
			if media_length == 0: return
			percent = float((current_time / media_length)) * 100
			seekable = (int(current_time) > 180 and (percent < 85))
			if seekable:
				trakt.scrobbleMovie(imdb, tmdb, percent) if media_type == 'movie' else trakt.scrobbleEpisode(imdb, tmdb, tvdb, season, episode, percent)
			if percent >= 85:
				trakt.scrobbleReset(imdb, tvdb, season, episode, refresh=False)
		except:
			log_utils.error()