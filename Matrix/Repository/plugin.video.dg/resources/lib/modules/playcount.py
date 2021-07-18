# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from resources.lib.modules.control import setting as getSetting, refresh as containerRefresh, addonInfo, progressDialogBG, monitor
from resources.lib.modules import trakt

traktIndicators = trakt.getTraktIndicatorsInfo()
tmdb_api_key = '3320855e65a9758297fec4f7c9717698'
omdb_api_key = 'd4daa2b'
tvdb_api_key = '7M8LCM0IEF8DOKNW'

def getMovieIndicators(refresh=False):
	try:
		if traktIndicators:
			if not refresh: timeout = 720
			elif trakt.getWatchedActivity() < trakt.timeoutsyncMovies(): timeout = 720
			else: timeout = 0
			indicators = trakt.cachesyncMovies(timeout=timeout)
			return indicators
		else:
			check_metahandler()
			indicators = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			return indicators
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def getTVShowIndicators(refresh=False):
	try:
		if traktIndicators:
			if not refresh: timeout = 720
			elif trakt.getWatchedActivity() < trakt.timeoutsyncTVShows(): timeout = 720
			else: timeout = 0
			indicators = trakt.cachesyncTVShows(timeout=timeout)
			return indicators
		else:
			check_metahandler()
			indicators = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			return indicators
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def getSeasonIndicators(imdb, refresh=False):
	try:
		if traktIndicators:
			if not refresh: timeout = 720
			if trakt.getWatchedActivity() < trakt.timeoutsyncSeason(imdb=imdb): timeout = 720
			else: timeout = 0
			indicators = trakt.cachesyncSeason(imdb=imdb, timeout=timeout)
			return indicators
		else:
			check_metahandler()
			indicators = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			return indicators
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def getMovieOverlay(indicators, imdb):
	if not indicators: return '4'
	try:
		if traktIndicators:
			playcount = [i for i in indicators if i == imdb]
			playcount = 5 if len(playcount) > 0 else 4
			return str(playcount)
		else:
			playcount = indicators._get_watched('movie', imdb, '', '')
			return str(playcount)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return '4'

def getTVShowOverlay(indicators, imdb, tvdb):
	if not indicators: return '4'
	try:
		if traktIndicators:
			playcount = [i[0] for i in indicators if i[0] == tvdb and len(i[2]) >= int(i[1])]
			playcount = 5 if len(playcount) > 0 else 4
			return str(playcount)
		else:
			playcount = indicators._get_watched('tvshow', imdb, '', '')
			return str(playcount)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return '4'

def getSeasonOverlay(indicators, imdb, tvdb, season):
	if not indicators: return '4'
	try:
		if traktIndicators:
			playcount = [i for i in indicators if int(season) == int(i)]
			playcount = 5 if len(playcount) > 0 else 4
			return str(playcount)
		else:
			playcount = indicators._get_watched('season', imdb, '', season)
			return str(playcount)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return '4'

def getEpisodeOverlay(indicators, imdb, tvdb, season, episode):
	if not indicators: return '4'
	try:
		if traktIndicators:
			playcount = [i[2] for i in indicators if i[0] == tvdb]
			playcount = playcount[0] if len(playcount) > 0 else []
			playcount = [i for i in playcount if int(season) == int(i[0]) and int(episode) == int(i[1])]
			playcount = 5 if len(playcount) > 0 else 4
			return str(playcount)
		else:
			playcount = indicators._get_watched_episode({'imdb_id': imdb, 'season': season, 'episode': episode, 'premiered': ''})
			return str(playcount)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return '4'

def getShowCount(indicators, imdb, tvdb):
	if not imdb.startswith('tt'): return None
	try:
		if traktIndicators:
			if indicators and tvdb in str(indicators):
				for indicator in indicators:
					if indicator[0] == tvdb:
						total = indicator[1]
						watched = len(indicator[2])
						unwatched = total - watched
						return {'total': total, 'watched': watched, 'unwatched': unwatched}
			else:
				result = trakt.showCount(imdb) # TMDb has "total_episodes" now so return None for unwatched shows and use that
				return result
		else:
			return None # this code below for metahandler does not aply here nor does the addon offer a means to return such counts
			if not indicators: return None
			for indicator in indicators:
				if indicator[0] == tvdb:
					total = indicator[1]
					watched = len(indicator[2])
					unwatched = total - watched
					return {'total': total, 'watched': watched, 'unwatched': unwatched}
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None

def getSeasonCount(imdb, season=None, season_special=False):
	if not imdb.startswith('tt'): return None
	try:
		if not traktIndicators: return None
		result = trakt.seasonCount(imdb=imdb)
		if not result: return None
		if not season: return result
		else:
			if getSetting('tv.specials') == 'true' and season_special: result = result[int(season)]
			else:
				if int(season) > len(result): return None
				result = result[int(season) - 1]
			return result
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None

def markMovieDuringPlayback(imdb, watched):
	try:
		if traktIndicators:
			if int(watched) == 5: trakt.markMovieAsWatched(imdb)
			else: trakt.markMovieAsNotWatched(imdb)
			trakt.cachesyncMovies()
			# if trakt.getTraktAddonMovieInfo():
				# trakt.markMovieAsNotWatched(imdb)
		else:
			check_metahandler()
			metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			metaget.get_meta('movie', name='', imdb_id=imdb)
			metaget.change_watched('movie', name='', imdb_id=imdb, watched=int(watched))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def markEpisodeDuringPlayback(imdb, tvdb, season, episode, watched):
	try:
		if traktIndicators:
			if int(watched) == 5: trakt.markEpisodeAsWatched(imdb, tvdb, season, episode)
			else: trakt.markEpisodeAsNotWatched(imdb, tvdb, season, episode)
			trakt.cachesyncTVShows()
			# if trakt.getTraktAddonEpisodeInfo():
				# trakt.markEpisodeAsNotWatched(imdb, tvdb, season, episode)
		else:
			check_metahandler()
			metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			metaget.get_meta('tvshow', name='', imdb_id=imdb)
			metaget.get_episode_meta('', imdb_id=imdb, season=season, episode=episode)
			metaget.change_watched('episode', '', imdb_id=imdb, season=season, episode=episode, watched=int(watched))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def movies(name, imdb, watched):
	try:
		if traktIndicators:
			if int(watched) == 5: trakt.watch(name=name, imdb=imdb, refresh=True)
			else: trakt.unwatch(name=name, imdb=imdb, refresh=True)
		else:
			check_metahandler()
			metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			metaget.get_meta('movie', name=name, imdb_id=imdb)
			metaget.change_watched('movie', name=name, imdb_id=imdb, watched=int(watched))
			containerRefresh()
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def episodes(name, imdb, tvdb, season, episode, watched):
	try:
		if traktIndicators:
			if int(watched) == 5: trakt.watch(name=name, imdb=imdb, tvdb=tvdb, season=season, episode=episode, refresh=True)
			else: trakt.unwatch(name=name, imdb=imdb, tvdb=tvdb, season=season, episode=episode, refresh=True)
		else:
			check_metahandler()
			metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			metaget.get_meta('tvshow', name=name, imdb_id=imdb)
			metaget.get_episode_meta(name, imdb_id=imdb, season=season, episode=episode)
			metaget.change_watched('episode', '', imdb_id=imdb, season=season, episode=episode, watched=int(watched))
			tvshowsUpdate(imdb=imdb, tvdb=tvdb) # control.refresh() done in this function
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def seasons(tvshowtitle, imdb, tvdb, season, watched):
	tvshows(tvshowtitle=tvshowtitle, imdb=imdb, tvdb=tvdb, season=season, watched=watched)

def tvshows(tvshowtitle, imdb, tvdb, season, watched):
	watched = int(watched)
	try:
		if traktIndicators:
			if watched == 5: trakt.watch(name=tvshowtitle, imdb=imdb, tvdb=tvdb, season=season, refresh=True)
			else: trakt.unwatch(name=tvshowtitle, imdb=imdb, tvdb=tvdb, season=season, refresh=True)
		else:
			check_metahandler()
			from resources.lib.menus import episodes
			from sys import exit as sysexit

			name = addonInfo('name')
			dialog = progressDialogBG
			dialog.create(str(name), str(tvshowtitle))
			dialog.update(0, str(name), str(tvshowtitle))

			metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
			metaget.get_meta('tvshow', name='', imdb_id=imdb)

			items = episodes.Episodes().get(tvshowtitle, '0', imdb, tvdb, create_directory = False)
			for i in range(len(items)):
				items[i]['season'] = int(items[i]['season'])
				items[i]['episode'] = int(items[i]['episode'])
			try: items = [i for i in items if int('%01d' % int(season)) == int('%01d' % i['season'])]
			except: pass

			items = [{'label': '%s S%02dE%02d' % (tvshowtitle, i['season'], i['episode']), 'season': int('%01d' % i['season']), 'episode': int('%01d' % i['episode'])} for i in items]
			count = len(items)
			for i in range(count):
				if monitor.abortRequested(): return sysexit()
				dialog.update(int(100.0 / count * i), str(name), str(items[i]['label']))
				season, episode = items[i]['season'], items[i]['episode']
				metaget.get_episode_meta('', imdb_id=imdb, season=season, episode=episode)
				metaget.change_watched('episode', '', imdb_id=imdb, season=season, episode=episode, watched=watched)
			tvshowsUpdate(imdb=imdb, tvdb=tvdb)

			try: dialog.close()
			except: pass
			del dialog
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def tvshowsUpdate(imdb, tvdb):
	try:
		if traktIndicators: return
		check_metahandler()
		from resources.lib.menus import episodes

		name = addonInfo('name')
		metaget = metahandlers.MetaData(tmdb_api_key, omdb_api_key, tvdb_api_key)
		metaget.get_meta('tvshow', name='', imdb_id=imdb)

		items = episodes.Episodes().get('', '0', imdb, '0', tvdb, create_directory=False)
		for i in range(len(items)):
			items[i]['season'] = int(items[i]['season'])
			items[i]['episode'] = int(items[i]['episode'])

		seasons = {}
		for i in items:
			if i['season'] not in seasons: seasons[i['season']] = []
			seasons[i['season']].append(i)

		countSeason = 0
		metaget.get_seasons('', imdb, seasons.keys()) # Must be called to initialize the database.

		for key, value in iter(seasons.items()):
			countEpisode = 0
			for i in value:
				countEpisode += int(metaget._get_watched_episode({'imdb_id': i['imdb'], 'season': i['season'], 'episode': i['episode'], 'premiered': ''}) == 5)
			countSeason += int(countEpisode == len(value))
			metaget.change_watched('season', '', imdb_id=imdb, season=key, watched = 5 if countEpisode == len(value) else 4)
		metaget.change_watched('tvshow', '', imdb_id=imdb, watched = 5 if countSeason == len(seasons.keys()) else 4)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	containerRefresh()

def check_metahandler():
	if not control.condVisibility('System.HasAddon(script.module.metahandler)'):
		control.execute('InstallAddon(script.module.metahandler)')
	try: from metahandler import metahandlers
	except: pass

