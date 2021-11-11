# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime
from json import dumps as jsdumps, loads as jsloads
import re
from urllib.parse import quote_plus
from resources.lib.database import cache
from resources.lib.indexers import tmdb as tmdb_indexer, fanarttv
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules.playcount import getSeasonIndicators, getSeasonOverlay, getSeasonCount
from resources.lib.modules import trakt
from resources.lib.modules import views


class Seasons:
	def __init__(self):
		self.list = []
		self.lang = control.apiLanguage()['tmdb']
		self.enable_fanarttv = control.setting('enable.fanarttv') == 'true'
		self.prefer_tmdbArt = control.setting('prefer.tmdbArt') == 'true'
		self.season_special = False
		self.date_time = datetime.now()
		self.today_date = (self.date_time).strftime('%Y-%m-%d')
		self.tmdb_poster_path = 'https://image.tmdb.org/t/p/w342'
		self.trakt_user = control.setting('trakt.username').strip()
		self.traktCredentials = trakt.getTraktCredentialsInfo()
		# self.traktwatchlist_link = 'https://api.trakt.tv/users/me/watchlist/seasons'
		# self.traktlists_link = 'https://api.trakt.tv/users/me/lists'
		self.showunaired = control.setting('showunaired') == 'true'
		self.unairedcolor = control.getColor(control.setting('unaired.identify'))
		self.showspecials = control.setting('tv.specials') == 'true'

	def get(self, tvshowtitle, year, imdb, tmdb, tvdb, art, idx=True, create_directory=True): # may need to add a cache duration over-ride param to pass
		self.list = []
		if idx:
			self.list = cache.get(self.tmdb_list, 96, tvshowtitle, imdb, tmdb, tvdb, art)
			if self.list is None: self.list = []
			if create_directory: self.seasonDirectory(self.list)
			return self.list
		else:
			self.list = self.tmdb_list(tvshowtitle, imdb, tmdb, tvdb, art)
			return self.list

	def tmdb_list(self, tvshowtitle, imdb, tmdb, tvdb, art):
		if not tmdb and (imdb or tvdb):
			try:
				result = cache.get(tmdb_indexer.TVshows().IdLookup, 96, imdb, tvdb)
				tmdb = str(result.get('id')) if result else ''
			except:
				if control.setting('debug.level') != '1': return
				from resources.lib.modules import log_utils
				return log_utils.log('tvshowtitle: (%s) missing tmdb_id: ids={imdb: %s, tmdb: %s, tvdb: %s}' % (tvshowtitle, imdb, tmdb, tvdb), __name__, log_utils.LOGDEBUG) # log TMDb shows that they do not have
		showSeasons = cache.get(tmdb_indexer.TVshows().get_showSeasons_meta, 96, tmdb)
		if not showSeasons: return
		if art: art = jsloads(art) # prob better off leaving this as it's own dict so seasonDirectory list builder can just pull that out and pass to .setArt()
		for item in showSeasons['seasons']: # seasons not parsed in tmdb module so ['seasons'] here is direct json response
			try:
				if not self.showspecials and item['season_number'] == 0: continue
				values = {}
				values.update(showSeasons)
				values['mediatype'] = 'season'
				values['premiered'] = str(item.get('air_date', '')) if item.get('air_date') else ''
				values['year'] = showSeasons['year'] # use show year not season year.  In seasonDirecotry send InfoLabels year pulled from premiered only.
				values['unaired'] = ''
				try:
					if values['status'].lower() == 'ended': pass # season level unaired
					elif not values['premiered']:
						values['unaired'] = 'true'
						if not self.showunaired: continue
						pass
					elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
						values['unaired'] = 'true'
						if not self.showunaired: continue
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
				values['total_episodes'] = item['episode_count'] # will be total for the specific season only
				values['season_title'] = item['name']
				values['plot'] = item['overview'] or showSeasons['plot']
				try: values['poster'] = self.tmdb_poster_path + item['poster_path']
				except: values['poster'] = ''
				if not values['poster'] and art: values['poster'] = art['poster'] if 'poster' in art else ''
				values['season_poster'] = values['poster']
				values['season'] = str(int(item['season_number']))
				if self.enable_fanarttv: values['season_poster2'] = fanarttv.get_season_poster(tvdb, values['season'])
				if art:
					values['fanart'] = art['fanart']
					values['icon'] = art['icon']
					values['thumb'] = art['thumb'] # thumb here is show_poster from show level TMDb module
					values['banner'] = art['banner']
					values['clearlogo'] = art['clearlogo']
					values['clearart'] = art['clearart']
					values['landscape'] = art['landscape']
					values['tvshow.poster'] = art['tvshow.poster'] # not used in seasonDirectory() atm
				for k in ('seasons',): values.pop(k, None) # pop() keys from showSeasons that are not needed anymore
				self.list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return self.list

	def seasonDirectory(self, items):
		from sys import argv # some functions like ActivateWindow() throw invalid handle less this is imported here.
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32054, message=33049)
		sysaddon, syshandle = argv[0], int(argv[1])
		is_widget = 'plugin' not in control.infoLabel('Container.PluginName')
		settingFanart = control.setting('fanart') == 'true'
		addonPoster, addonFanart, addonBanner = control.addonPoster(), control.addonFanart(), control.addonBanner()
		try: indicators = getSeasonIndicators(items[0]['imdb'], refresh=True)
		except: indicators = None
		unwatchedEnabled = control.setting('tvshows.unwatched.enabled') == 'true'
		if trakt.getTraktIndicatorsInfo():
			watchedMenu, unwatchedMenu = control.lang(32068), control.lang(32069)
		else:
			watchedMenu, unwatchedMenu = control.lang(32066), control.lang(32067)
		traktManagerMenu, queueMenu = control.lang(32070), control.lang(32065)
		showPlaylistMenu, clearPlaylistMenu = control.lang(35517), control.lang(35516)
		labelMenu, playRandom = control.lang(32055), control.lang(32535)
		addToLibrary = control.lang(32551)
		try: multi = [i['tvshowtitle'] for i in items]
		except: multi = []
		multi = True if len([x for y,x in enumerate(multi) if x not in multi[:y]]) > 1 else False
		for i in items:
			try:
				title, imdb, tmdb, tvdb, year, season = i.get('tvshowtitle'), i.get('imdb', ''), i.get('tmdb', ''), i.get('tvdb', ''), i.get('year', ''), i.get('season')
				label = '%s %s' % (labelMenu, season)
				if not self.season_special and self.showspecials:
					self.season_special = True if int(season) == 0 else False
				try:
					if i['unaired'] == 'true': label = '[COLOR %s][I]%s[/I][/COLOR]' % (self.unairedcolor, label)
				except: pass
				systitle = quote_plus(title)
				meta = dict((k, v) for k, v in iter(i.items()) if v is not None and v != '')
				# setting mediatype to "season" causes "Infomation" and "play trailer" to not be available in some skins
				meta.update({'code': imdb, 'imdbnumber': imdb, 'mediatype': 'tvshow', 'tag': [imdb, tmdb]}) # "tag" and "tagline" for movies only, but works in my skin mod so leave
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass

				poster = meta.get('tvshow.poster') or addonPoster # tvshow.poster
				if self.prefer_tmdbArt: season_poster = meta.get('season_poster') or meta.get('season_poster2') or poster
				else: season_poster = meta.get('season_poster2') or meta.get('season_poster') or poster
				fanart = ''
				if settingFanart: fanart = meta.get('fanart') or addonFanart
				icon = meta.get('icon') or poster
				banner = meta.get('banner') or addonBanner
				art = {}
				art.update({'poster': season_poster, 'tvshow.poster': poster, 'season.poster': season_poster, 'fanart': fanart, 'icon': icon, 'thumb': season_poster, 'banner': banner,
						'clearlogo': meta.get('clearlogo', ''), 'tvshow.clearlogo': meta.get('clearlogo', ''), 'clearart': meta.get('clearart', ''), 'tvshow.clearart': meta.get('clearart', ''), 'landscape': meta.get('landscape')})
				# for k in ('poster2', 'poster3', 'fanart2', 'fanart3', 'banner2', 'banner3'): meta.pop(k, None)
				meta.update({'poster': poster, 'fanart': fanart, 'banner': banner, 'thumb': season_poster, 'season_poster': season_poster, 'icon': icon})
####-Context Menu and Overlays-####
				cm = []
				try:
					overlay = int(getSeasonOverlay(indicators, imdb, tvdb, season))
					watched = (overlay == 5)
					if self.traktCredentials:
						cm.append((traktManagerMenu, 'RunPlugin(%s?action=tools_traktManager&name=%s&imdb=%s&tvdb=%s&season=%s&watched=%s)' % (sysaddon, systitle, imdb, tvdb, season, watched)))
					if watched:
						meta.update({'playcount': 1, 'overlay': 5})
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=playcount_TVShow&name=%s&imdb=%s&tvdb=%s&season=%s&query=4)' % (sysaddon, systitle, imdb, tvdb, season)))
					else: 
						meta.update({'playcount': 0, 'overlay': 4})
						cm.append((watchedMenu, 'RunPlugin(%s?action=playcount_TVShow&name=%s&imdb=%s&tvdb=%s&season=%s&query=5)' % (sysaddon, systitle, imdb, tvdb, season)))
				except: pass
				sysmeta = quote_plus(jsdumps(meta))
				cm.append((playRandom, 'RunPlugin(%s?action=play_Random&rtype=episode&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&meta=%s&season=%s)' % (sysaddon, systitle, year, imdb, tmdb, tvdb, sysmeta, season)))
				cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem&name=%s)' % (sysaddon, systitle)))
				cm.append((showPlaylistMenu, 'RunPlugin(%s?action=playlist_Show)' % sysaddon))
				cm.append((clearPlaylistMenu, 'RunPlugin(%s?action=playlist_Clear)' % sysaddon))
				cm.append((addToLibrary, 'RunPlugin(%s?action=library_tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s)' % (sysaddon, systitle, year, imdb, tmdb, tvdb)))
				cm.append(('[COLOR ghostwhite]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
####################################
				url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&meta=%s&season=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, sysmeta, season)
				item = control.item(label=label, offscreen=True)
				if 'castandart' in i: item.setCast(i['castandart'])
				item.setArt(art)
				if unwatchedEnabled:
					try:
						count = getSeasonCount(imdb, season, self.season_special) # self.season_special is just a flag to set if a season special exists and we are set to show it
						if count:
							item.setProperties({'WatchedEpisodes': str(count['watched']), 'UnWatchedEpisodes': str(count['unwatched'])})
						else: item.setProperties({'WatchedEpisodes': '0', 'UnWatchedEpisodes': str(meta.get('counts', {}).get(str(season), ''))}) # temp use TMDb's season-episode count for threads not finished....next load counts will update with trakt data
					except: pass
				try: item.setProperties({'TotalSeasons': str(meta.get('total_seasons', '')), 'TotalEpisodes': str(meta.get('total_episodes', ''))})
				except: pass
				if is_widget: item.setProperty('isDG_widget', 'true')
				try: # Year is the shows year, not the seasons year. Extract year from premier date for InfoLabels to have "season_year".
					season_year = re.findall(r'(\d{4})', i.get('premiered', ''))[0]
					meta.update({'year': season_year})
				except: pass
				item.setUniqueIDs({'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb})
				item.setProperty('IsPlayable', 'false')
				item.setInfo(type='video', infoLabels=control.metadataClean(meta))
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		try: control.property(syshandle, 'showplot', items[0]['plot'])
		except: pass
		control.content(syshandle, 'seasons')
		control.directory(syshandle, cacheToDisc=True)
		views.setView('seasons', {'skin.estuary': 55, 'skin.confluence': 500})