# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime
from json import dumps as jsdumps, loads as jsloads
import re
import threading
from time import time, sleep
from urllib.parse import urljoin
from resources.lib.database import cache, traktsync
from resources.lib.modules import cleandate
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import utils

BASE_URL = 'https://api.trakt.tv'
# Venom trakt app
# V2_API_KEY = 'c622fa66e6cdd783b23f2fc1a1abedc1f1e6ea739d8755248487d1dcfeda66e5'
# CLIENT_SECRET = '3430dbd20bd3eb55c0f4e3dc05c7cbbadaf1fd4b8e2a572f4200e482a2041bd8'
# My Accounts trakt app
V2_API_KEY = '1ff09b52d009f286be2d9bdfc0314c688319cbf931040d5f8847e7694a01de42'
CLIENT_SECRET = '0c5134e5d15b57653fefed29d813bfbd58d73d51fb9bcd6442b5065f30c4d4dc'
headers = {'Content-Type': 'application/json', 'trakt-api-key': V2_API_KEY, 'trakt-api-version': '2'}
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
databaseName = control.cacheFile
databaseTable = 'trakt'
highlight_color = control.getColor(control.setting('highlight.color'))

def getTrakt(url, post=None, extended=False):
	try:
		if not url.startswith(BASE_URL): url = urljoin(BASE_URL, url)
		if post: post = jsdumps(post)
		if not getTraktCredentialsInfo():
			return client.request(url, post=post, headers=headers)

		# headers['Authorization'] = 'Bearer %s' % control.setting('trakt.token')
		headers['Authorization'] = 'Bearer %s' % control.addon('script.module.myaccounts').getSetting('trakt.token')

		result = client.request(url, post=post, headers=headers, output='extended', error=True)
		# result = utils.byteify(result) # check if this is needed because client "as_bytes" should handle this
		try: code = str(result[1]) # result[1] is already a str from client module
		except: code = ''

		if code.startswith('5') or (result and isinstance(result, str) and '<html' in result) or not result: # covers Maintenance html responses ["Bad Gateway", "We're sorry, but something went wrong (500)"])
			log_utils.log('Temporary Trakt Server Problems', level=log_utils.LOGINFO)
			control.notification(title=32315, message=33676)
			return None
		elif result and code in ['423']:
			log_utils.log('Locked User Account - Contact Trakt Support: %s' % str(result[0]), level=log_utils.LOGWARNING)
			control.notification(title=32315, message=33675)
			return None
		elif result and code in ['404']:
			log_utils.log('Request Not Found: url=(%s): %s' % (url, str(result[0])), level=log_utils.LOGWARNING)
			return None
		elif result and code in ['429']:
			if 'Retry-After' in result[2]: # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME (1000 calls every 5 minutes, doubt we'll ever hit that)
				throttleTime = result[2]['Retry-After']
				control.notification(title=32315, message='Trakt Throttling Applied, Sleeping for %s seconds' % throttleTime) # message ang code 33674
				control.sleep((int(throttleTime) + 1) * 1000)
				return getTrakt(url, post=post, extended=extended)
		elif result and code in ['401']: # Re-Auth token
			success = re_auth(headers)
			if success: return getTrakt(url, post=post, extended=extended)
		if result and code not in ['401', '405']:
			if extended: return result[0], result[2]
			else: return result[0]
	except:
		log_utils.error('getTrakt Error: ')
	return None

def getTraktAsJson(url, post=None):
	try:
		res_headers = {}
		r = getTrakt(url=url, post=post, extended=True)
		if isinstance(r, tuple) and len(r) == 2:
			r , res_headers = r[0], r[1]
		if not r: return
		r = utils.json_loads_as_str(r)
		res_headers = dict((k.lower(), v) for k, v in iter(res_headers.items()))
		if 'x-sort-by' in res_headers and 'x-sort-how' in res_headers:
			r = sort_list(res_headers['x-sort-by'], res_headers['x-sort-how'], r)
		return r
	except:
		log_utils.error()

def re_auth(headers):
	try:
		ma_token = control.addon('script.module.myaccounts').getSetting('trakt.token')
		ma_refresh = control.addon('script.module.myaccounts').getSetting('trakt.refresh')
		if ma_token != control.setting('trakt.token') or ma_refresh != control.setting('trakt.refresh'):
			log_utils.log('Syncing My Accounts Trakt Token', level=log_utils.LOGINFO)
			from resources.lib.modules import my_accounts
			my_accounts.syncMyAccounts(silent=True)
			return True

		log_utils.log('Re-Authenticating Trakt Token', level=log_utils.LOGINFO)
		oauth = urljoin(BASE_URL, '/oauth/token')
		# opost = {'client_id': V2_API_KEY, 'client_secret': CLIENT_SECRET, 'redirect_uri': REDIRECT_URI, 'grant_type': 'refresh_token', 'refresh_token': control.setting('trakt.refresh')}
		opost = {'client_id': V2_API_KEY, 'client_secret': CLIENT_SECRET, 'redirect_uri': REDIRECT_URI, 'grant_type': 'refresh_token', 'refresh_token': control.addon('script.module.myaccounts').getSetting('trakt.refresh')}

		result = client.request(oauth, post=jsdumps(opost), headers=headers, error=True)
		# result = utils.byteify(result) # check if this is needed because client "as_bytes" should handle this
		try: code = str(result[1])
		except: code = ''

		if code.startswith('5') or (result and isinstance(result, str) and '<html' in result) or not result: # covers Maintenance html responses ["Bad Gateway", "We're sorry, but something went wrong (500)"])
			log_utils.log('Temporary Trakt Server Problems', level=log_utils.LOGINFO)
			control.notification(title=32315, message=33676)
			return False
		elif result and code in ['423']:
			log_utils.log('Locked User Account - Contact Trakt Support: %s' % str(result[0]), level=log_utils.LOGINFO)
			control.notification(title=32315, message=33675)
			return False

		if result and code not in ['401', '405']:
			try: result = jsloads(result) # result = utils.json_loads_as_str(result) # which json method here?
			except:
				log_utils.error()
				return False
			if 'error' in result and result['error'] == 'invalid_grant':
				log_utils.log('Please Re-Authorize your Trakt Account: %s' % result['error'], __name__, level=log_utils.LOGWARNING)
				control.notification(title=32315, message=33677)
				return False

			token, refresh = result['access_token'], result['refresh_token']
			expires = str(time() + 7776000)
			control.setSetting('trakt.token', token)
			control.setSetting('trakt.refresh', refresh)
			control.setSetting('trakt.expires', expires)
			control.addon('script.module.myaccounts').setSetting('trakt.token', token)
			control.addon('script.module.myaccounts').setSetting('trakt.refresh', refresh)
			control.addon('script.module.myaccounts').setSetting('trakt.expires', expires)
			log_utils.log('Trakt Token Successfully Re-Authorized', level=log_utils.LOGDEBUG)
			return True
		else:
			log_utils.log('Error while Re-Authorizing Trakt Token: %s' % str(result[0]), level=log_utils.LOGWARNING)
			return False
	except:
		log_utils.error()

def authTrakt():
	try:
		if getTraktCredentialsInfo():
			if control.yesnoDialog(control.lang(32511), control.lang(32512), '', 'Trakt'):
				control.setSetting('trakt.isauthed', '')
				control.setSetting('trakt.username', '')
				control.setSetting('trakt.token', '')
				control.setSetting('trakt.refresh', '')
				control.setSetting('trakt.expires', '')
			raise Exception()
		result = getTraktAsJson('/oauth/device/code', {'client_id': V2_API_KEY})
		verification_url = (control.lang(32513) % result['verification_url'])
		user_code = (control.lang(32514) % result['user_code'])
		expires_in = int(result['expires_in'])
		device_code = result['device_code']
		interval = result['interval']
		progressDialog = control.progressDialog
		progressDialog.create('Trakt', verification_url, user_code)

		for i in range(0, expires_in):
			try:
				if progressDialog.iscanceled(): break
				sleep(1)
				if not float(i) % interval == 0: continue
				r = getTraktAsJson('/oauth/device/token', {'client_id': V2_API_KEY, 'client_secret': CLIENT_SECRET, 'code': device_code})
				if not r: continue
				if 'access_token' in r: break
			except:
				log_utils.error()
		try: progressDialog.close()
		except: pass

		token, refresh = r['access_token'], r['refresh_token']
		headers = {'Content-Type': 'application/json', 'trakt-api-key': V2_API_KEY, 'trakt-api-version': '2', 'Authorization': 'Bearer %s' % token}

		result = client.request(urljoin(BASE_URL, '/users/me'), headers=headers)
		result = utils.json_loads_as_str(result)
		username = result['username']
		expires = str(time() + 7776000)

		control.setSetting('trakt.isauthed', 'true')
		control.setSetting('trakt.username', username)
		control.setSetting('trakt.token', token)
		control.setSetting('trakt.refresh', refresh)
		control.setSetting('trakt.expires', expires)
		raise Exception()
	except:
		log_utils.error()

def getTraktCredentialsInfo():
	username = control.setting('trakt.username').strip()
	token = control.setting('trakt.token')
	refresh = control.setting('trakt.refresh')
	if (username == '' or token == '' or refresh == ''):
		return False
	return True

def getTraktIndicatorsInfo():
	indicators = control.setting('indicators') if not getTraktCredentialsInfo() else control.setting('indicators.alt')
	indicators = True if indicators == '1' else False
	return indicators

def getTraktAddonMovieInfo():
	try: scrobble = control.addon('script.trakt').getSetting('scrobble_movie')
	except: scrobble = ''
	try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
	except: ExcludeHTTP = ''
	try: authorization = control.addon('script.trakt').getSetting('authorization')
	except: authorization = ''
	if scrobble == 'true' and ExcludeHTTP == 'false' and authorization != '':
		return True
	else: return False

def getTraktAddonEpisodeInfo():
	try: scrobble = control.addon('script.trakt').getSetting('scrobble_episode')
	except: scrobble = ''
	try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
	except: ExcludeHTTP = ''
	try: authorization = control.addon('script.trakt').getSetting('authorization')
	except: authorization = ''
	if scrobble == 'true' and ExcludeHTTP == 'false' and authorization != '':
		return True
	else: return False

def watch(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True):
	control.busy()
	if not tvdb:
		markMovieAsWatched(imdb)
		cachesyncMovies()
	elif episode:
		markEpisodeAsWatched(imdb, tvdb, season, episode)
		cachesyncTV(imdb)
	elif season:
		markSeasonAsWatched(imdb, tvdb, season)
		cachesyncTV(imdb)
	elif tvdb:
		markTVShowAsWatched(imdb, tvdb)
		cachesyncTV(imdb)
	else:
		markMovieAsWatched(imdb)
		cachesyncMovies()
	control.hide()
	if refresh: control.refresh()
	control.trigger_widget_refresh()
	if control.setting('trakt.general.notifications') == 'true':
		if season and not episode: name = '%s-Season%s...' % (name, season)
		if season and episode: name = '%s-S%sxE%02d...' % (name, season, int(episode))
		control.notification(title=32315, message=control.lang(35502) % name)

def unwatch(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True):
	control.busy()
	if not tvdb:
		markMovieAsNotWatched(imdb)
		cachesyncMovies()
	elif episode:
		markEpisodeAsNotWatched(imdb, tvdb, season, episode)
		cachesyncTV(imdb)
	elif season:
		markSeasonAsNotWatched(imdb, tvdb, season)
		cachesyncTV(imdb)
	elif tvdb:
		markTVShowAsNotWatched(imdb, tvdb)
		cachesyncTV(imdb)
	else:
		markMovieAsNotWatched(imdb)
		cachesyncMovies()
	control.hide()
	if refresh: control.refresh()
	control.trigger_widget_refresh()
	if control.setting('trakt.general.notifications') == 'true':
		if season and not episode: name = '%s-Season%s...' % (name, season)
		if season and episode: name = '%s-S%sxE%02d...' % (name, season, int(episode))
		control.notification(title=32315, message=control.lang(35503) % name)

def rate(imdb=None, tvdb=None, season=None, episode=None):
	return _rating(action='rate', imdb=imdb, tvdb=tvdb, season=season, episode=episode)

def unrate(imdb=None, tvdb=None, season=None, episode=None):
	return _rating(action='unrate', imdb=imdb, tvdb=tvdb, season=season, episode=episode)

def rateShow(imdb=None, tvdb=None, season=None, episode=None):
	if control.setting('trakt.rating') == 1:
		rate(imdb=imdb, tvdb=tvdb, season=season, episode=episode)

def _rating(action, imdb=None, tvdb=None, season=None, episode=None):
	control.busy()
	try:
		addon = 'script.trakt'
		if control.condVisibility('System.HasAddon(%s)' % addon):
			import imp
			# from importlib import import_module ?
			data = {}
			data['action'] = action
			if tvdb:
				data['video_id'] = tvdb
				if episode:
					data['media_type'] = 'episode'
					data['dbid'] = 1
					data['season'] = int(season)
					data['episode'] = int(episode)
				elif season:
					data['media_type'] = 'season'
					data['dbid'] = 5
					data['season'] = int(season)
				else:
					data['media_type'] = 'show'
					data['dbid'] = 2
			else:
				data['video_id'] = imdb
				data['media_type'] = 'movie'
				data['dbid'] = 4
			script = control.joinPath(control.addonPath(addon), 'resources', 'lib', 'sqlitequeue.py')
			sqlitequeue = imp.load_source('sqlitequeue', script) # this may be deprecated
			data = {'action': 'manualRating', 'ratingData': data}
			sqlitequeue.SqliteQueue().append(data)
		else:
			control.notification(title=32315, message=33659)
		control.hide()
	except:
		log_utils.error()

def hideItem(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True):
	sections = ['progress_watched', 'calendar']
	sections_display = [control.lang(40072), control.lang(40073)]
	selection = control.selectDialog([i for i in sections_display], heading=control.addonInfo('name') + ' - ' + control.lang(40074))
	if selection == -1: return
	control.busy()
	section = sections[selection]
	if episode: post = {"shows": [{"ids": {"tvdb": tvdb}}]}
	else: post = {"movies": [{"ids": {"imdb": imdb}}]}
	getTrakt('users/hidden/%s' % section, post=post)[0]
	control.hide()
	if refresh: control.refresh()
	control.trigger_widget_refresh()
	if control.setting('trakt.general.notifications') == 'true':
		control.notification(title=32315, message=control.lang(33053) % (name, sections_display[selection]))

def manager(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True, watched=None):
	lists = []
	try:
		if season: season = int(season)
		if episode: episode = int(episode)
		media_type = 'Show' if tvdb else 'Movie'

		if watched is not None:
			if watched is True:
				items = [(control.lang(33652) % highlight_color, 'unwatch')]
			else:
				items = [(control.lang(33651) % highlight_color, 'watch')]
		else:
			items = [(control.lang(33651) % highlight_color, 'watch')]
			items += [(control.lang(33652) % highlight_color, 'unwatch')]
		if control.condVisibility('System.HasAddon(script.trakt)'):
			items += [(control.lang(33653) % highlight_color, 'rate')]
			items += [(control.lang(33654) % highlight_color, 'unrate')]
		items += [(control.lang(40075) % (highlight_color, media_type), 'hideItem')]
		if control.setting('trakt.scrobble') == 'true' and control.setting('resume.source') == '1':
			if media_type == 'Movie' or episode:
				items += [(control.lang(40076) % highlight_color, 'scrobbleReset')]
		if season or episode:
			items += [(control.lang(33573) % highlight_color, '/sync/watchlist')]
			items += [(control.lang(33574) % highlight_color, '/sync/watchlist/remove')]
		items += [(control.lang(33577) % highlight_color, '/sync/watchlist')]
		items += [(control.lang(33578) % highlight_color, '/sync/watchlist/remove')]
		items += [(control.lang(33575) % highlight_color, '/sync/collection')]
		items += [(control.lang(33576) % highlight_color, '/sync/collection/remove')]
		items += [(control.lang(33579), '/users/me/lists/%s/items')]

		result = getTraktAsJson('/users/me/lists')
		lists = [(i['name'], i['ids']['slug']) for i in result]
		lists = [lists[i//2] for i in range(len(lists)*2)]

		for i in range(0, len(lists), 2):
			lists[i] = ((control.lang(33580) % (highlight_color, lists[i][0])), '/users/me/lists/%s/items' % lists[i][1])
		for i in range(1, len(lists), 2):
			lists[i] = ((control.lang(33581) % (highlight_color, lists[i][0])), '/users/me/lists/%s/items/remove' % lists[i][1])
		items += lists

		control.hide()
		select = control.selectDialog([i[0] for i in items], heading=control.addonInfo('name') + ' - ' + control.lang(32515))

		if select == -1: return
		if select >= 0:
			if items[select][1] == 'watch':
				watch(name, imdb=imdb, tvdb=tvdb, season=season, episode=episode, refresh=refresh)
			elif items[select][1] == 'unwatch':
				unwatch(name, imdb=imdb, tvdb=tvdb, season=season, episode=episode, refresh=refresh)
			elif items[select][1] == 'rate':
				rate(imdb=imdb, tvdb=tvdb, season=season, episode=episode)
			elif items[select][1] == 'unrate':
				unrate(imdb=imdb, tvdb=tvdb, season=season, episode=episode)
			elif items[select][1] == 'hideItem':
				hideItem(name=name, imdb=imdb, tvdb=tvdb, season=season, episode=episode)
			elif items[select][1] == 'scrobbleReset':
				scrobbleReset(imdb=imdb, tvdb=tvdb, season=season, episode=episode, widgetRefresh=True)
			else:
				if not tvdb:
					post = {"movies": [{"ids": {"imdb": imdb}}]}
				else:
					if episode:
						if items[select][1] == '/sync/watchlist' or items[select][1] == '/sync/watchlist/remove':
							post = {"shows": [{"ids": {"tvdb": tvdb}}]}
						else:
							post = {"shows": [{"ids": {"tvdb": tvdb}, "seasons": [{"number": season, "episodes": [{"number": episode}]}]}]}
							name = name + ' - ' + '%sx%02d' % (season, episode)
					elif season:
						if items[select][1] == '/sync/watchlist' or items[select][1] == '/sync/watchlist/remove':
							post = {"shows": [{"ids": {"tvdb": tvdb}}]}
						else:
							post = {"shows": [{"ids": {"tvdb": tvdb}, "seasons": [{"number": season}]}]}
							name = name + ' - ' + 'Season %s' % season
					else: post = {"shows": [{"ids": {"tvdb": tvdb}}]}
				if items[select][1] == '/users/me/lists/%s/items':
					slug = listAdd(successNotification=True)
					if slug: getTrakt(items[select][1] % slug, post=post)[0]
				else:
					getTrakt(items[select][1], post=post)[0]
				control.hide()
				list = re.search('\[B](.+?)\[/B]', items[select][0]).group(1)
				message = control.lang(33583) if 'remove' in items[select][1] else control.lang(33582)
				if items[select][0].startswith('Add'): refresh = False
				control.hide()
				if refresh: control.refresh()
				control.trigger_widget_refresh()
				if control.setting('trakt.general.notifications') == 'true':
					control.notification(title=name, message=message + ' (%s)' % list)
	except:
		log_utils.error()
		control.hide()

def listAdd(successNotification=True):
	t = control.lang(32520)
	k = control.keyboard('', t) ; k.doModal()
	new = k.getText() if k.isConfirmed() else None
	if not new: return
	result = getTrakt('/users/me/lists', post = {"name" : new, "privacy" : "private"})
	try:
		slug = jsloads(result)['ids']['slug']
		if successNotification: control.notification(title=32070, message=33661)
		return slug
	except:
		control.notification(title=32070, message=33584)
		return None

def lists(id=None):
	return cache.get(getTraktAsJson, 48, 'https://api.trakt.tv/users/me/lists' + ('' if not id else ('/' + str(id))))

def list(id):
	return lists(id=id)

def slug(name):
	name = name.strip()
	name = name.lower()
	name = re.sub(r'[^a-z0-9_]', '-', name) # check apostrophe
	name = re.sub(r'--+', '-', name)
	return name

def getActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watched_at']) # added 8/30/20
		activity.append(i['movies']['collected_at'])
		activity.append(i['movies']['watchlisted_at'])
		activity.append(i['movies']['paused_at']) # added 8/30/20
		activity.append(i['movies']['hidden_at']) # added 4/02/21
		activity.append(i['episodes']['watched_at']) # added 8/30/20
		activity.append(i['episodes']['collected_at'])
		activity.append(i['episodes']['watchlisted_at'])
		activity.append(i['episodes']['paused_at']) # added 8/30/20
		activity.append(i['shows']['watchlisted_at'])
		activity.append(i['shows']['hidden_at']) # added 4/02/21
		activity.append(i['seasons']['watchlisted_at'])
		activity.append(i['seasons']['hidden_at']) # added 4/02/21
		activity.append(i['lists']['liked_at'])
		activity.append(i['lists']['updated_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getWatchedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watched_at'])
		activity.append(i['episodes']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getMoviesWatchedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getEpisodesWatchedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['episodes']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getCollectedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['collected_at'])
		activity.append(i['episodes']['collected_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getWatchListedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watchlisted_at'])
		activity.append(i['episodes']['watchlisted_at'])
		activity.append(i['shows']['watchlisted_at'])
		activity.append(i['seasons']['watchlisted_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getPausedActivity():
	try:
		i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['paused_at'])
		activity.append(i['episodes']['paused_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def cachesyncMovies(timeout=0):
	indicators = cache.get(syncMovies, timeout)
	return indicators

def sync_watched():
	try:
		while not control.monitor.abortRequested():
			moviesWatchedActivity = getMoviesWatchedActivity()
			db_movies_last_watched = timeoutsyncMovies()
			episodesWatchedActivity = getEpisodesWatchedActivity()
			db_episoodes_last_watched = timeoutsyncTVShows()
			if moviesWatchedActivity > db_movies_last_watched:
				log_utils.log('Trakt Watched Movie Sync Update...(local db latest "watched_at" = %s, trakt api latest "watched_at" = %s)' % \
								(str(db_movies_last_watched), str(moviesWatchedActivity)), __name__, log_utils.LOGDEBUG)
				cachesyncMovies()
			if episodesWatchedActivity > db_episoodes_last_watched:
				log_utils.log('Trakt Watched Episodes Sync Update...(local db latest "watched_at" = %s, trakt api latest "watched_at" = %s)' % \
								(str(db_episoodes_last_watched), str(episodesWatchedActivity)), __name__, log_utils.LOGDEBUG)
				cachesyncTVShows()
			if control.monitor.waitForAbort(60*15): break
	except:
		log_utils.error()

def timeoutsyncMovies():
	timeout = cache.timeout(syncMovies)
	return timeout

def syncMovies():
	try:
		if not getTraktCredentialsInfo(): return
		indicators = getTraktAsJson('/users/me/watched/movies')
		if not indicators: return None
		indicators = [i['movie']['ids'] for i in indicators]
		indicators = [str(i['imdb']) for i in indicators if 'imdb' in i]
		return indicators
	except:
		log_utils.error()

def watchedMovies():
	try:
		if not getTraktCredentialsInfo(): return
		return getTraktAsJson('/users/me/watched/movies?extended=full')
	except:
		log_utils.error()

def watchedMoviesTime(imdb):
	try:
		imdb = str(imdb)
		items = watchedMovies()
		for item in items:
			if str(item['movie']['ids']['imdb']) == imdb: return item['last_watched_at']
	except:
		log_utils.error()

def cachesyncTV(imdb):
	threads = [threading.Thread(target=cachesyncTVShows), threading.Thread(target=cachesyncSeason, args=(imdb,))]
	[i.start() for i in threads]
	[i.join() for i in threads]

def cachesyncTVShows(timeout=0):
	indicators = cache.get(syncTVShows, timeout)
	return indicators

def timeoutsyncTVShows():
	timeout = cache.timeout(syncTVShows)
	return timeout

def syncTVShows():
	try:
		if not getTraktCredentialsInfo(): return
		indicators = getTraktAsJson('/users/me/watched/shows?extended=full')
		if not indicators: return None
		indicators = [(i['show']['ids']['tvdb'], i['show']['aired_episodes'], sum([[(s['number'], e['number']) for e in s['episodes']] for s in i['seasons']], [])) for i in indicators]
		indicators = [(str(i[0]), int(i[1]), i[2]) for i in indicators]
		return indicators
	except:
		log_utils.error()

def watchedShows():
	try:
		if not getTraktCredentialsInfo(): return
		return getTraktAsJson('/users/me/watched/shows?extended=full')
	except:
		log_utils.error()

def watchedShowsTime(tvdb, season, episode):
	try:
		tvdb = str(tvdb)
		season = int(season)
		episode = int(episode)
		items = watchedShows()
		for item in items:
			if str(item['show']['ids']['tvdb']) == tvdb:
				seasons = item['seasons']
				for s in seasons:
					if s['number'] == season:
						episodes = s['episodes']
						for e in episodes:
							if e['number'] == episode:
								return e['last_watched_at']
	except:
		log_utils.error()

def cachesyncSeason(imdb, timeout=0):
	indicators = cache.get(syncSeason, timeout, imdb) # this is returning incorect values and not updating the cache
	return indicators

def timeoutsyncSeason(imdb):
	timeout = cache.timeout(syncSeason, imdb)
	return timeout

def syncSeason(imdb):
	try:
		if not getTraktCredentialsInfo(): return
		if control.setting('tv.specials') == 'true':
			indicators = getTraktAsJson('/shows/%s/progress/watched?specials=true&hidden=false&count_specials=true' % imdb)
		else:
			indicators = getTraktAsJson('/shows/%s/progress/watched?specials=false&hidden=false' % imdb)
		if not indicators: return None
		indicators = indicators['seasons']
		indicators = [(i['number'], [x['completed'] for x in i['episodes']]) for i in indicators]
		indicators = ['%01d' % int(i[0]) for i in indicators if False not in i[1]]
		return indicators
	except:
		log_utils.error()
		return None

def showCount(imdb, refresh=True, wait=False):
	try:
		if not imdb: return None
		if not imdb.startswith('tt'): return None
		result = {'total': 0, 'watched': 0, 'unwatched': 0}
		indicators = seasonCount(imdb=imdb, refresh=refresh, wait=wait)
		if not indicators: return None
		for indicator in indicators:
			result['total'] += indicator['total']
			result['watched'] += indicator['watched']
			result['unwatched'] += indicator['unwatched']
		return result
	except:
		log_utils.error()
		return None

def seasonCount(imdb, refresh=True, wait=False):
	try:
		if not imdb: return None
		if not imdb.startswith('tt'): return None
		indicators = cache.cache_existing(_seasonCountRetrieve, imdb) # get existing result while thread fetches new
		if refresh:
			thread = threading.Thread(target=_seasonCountCache, args=(imdb,))
			thread.start()
			if wait: # NB: Do not wait to retrieve a fresh count, otherwise loading show/season menus are slow.
				thread.join()
				indicators = cache.cache_existing(_seasonCountRetrieve, imdb)
		return indicators
	except:
		log_utils.error()
		return None

def _seasonCountCache(imdb):
	return cache.get(_seasonCountRetrieve, 0.3, imdb)
	# return cache.get(_seasonCountRetrieve, 0, imdb)

def _seasonCountRetrieve(imdb):
	try:
		if not getTraktCredentialsInfo(): return
		if control.setting('tv.specials') == 'true':
			indicators = getTraktAsJson('/shows/%s/progress/watched?specials=true&hidden=false&count_specials=true' % imdb)
		else:
			indicators = getTraktAsJson('/shows/%s/progress/watched?specials=false&hidden=false' % imdb)
		if not indicators: return None
		seasons = indicators['seasons']
		return [{'total': season['aired'], 'watched': season['completed'], 'unwatched': season['aired'] - season['completed']} for season in seasons]
		# return {season['number']: {'total': season['aired'], 'watched': season['completed'], 'unwatched': season['aired'] - season['completed']} for season in seasons}
	except:
		log_utils.error()
		return None

def markMovieAsWatched(imdb):
	if not imdb.startswith('tt'): imdb = 'tt' + imdb
	return getTrakt('/sync/history', {"movies": [{"ids": {"imdb": imdb}}]})[0]

def markMovieAsNotWatched(imdb):
	if not imdb.startswith('tt'): imdb = 'tt' + imdb
	return getTrakt('/sync/history/remove', {"movies": [{"ids": {"imdb": imdb}}]})[0]

def markTVShowAsWatched(imdb, tvdb):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	result = getTrakt('/sync/history', {"shows": [{"ids": {"tvdb": tvdb}}]})[0]
	seasonCount(imdb)
	return result

def markTVShowAsNotWatched(imdb, tvdb):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	result = getTrakt('/sync/history/remove', {"shows": [{"ids": {"tvdb": tvdb}}]})[0]
	seasonCount(imdb)
	return result

def markSeasonAsWatched(imdb, tvdb, season):
	try:
		if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
		season = int('%01d' % int(season))
		result = getTrakt('/sync/history', {"shows": [{"seasons": [{"number": season}], "ids": {"tvdb": tvdb}}]})[0]
		seasonCount(imdb)
		return result
	except:
		log_utils.error()

def markSeasonAsNotWatched(imdb, tvdb, season):
	try:
		if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
		season = int('%01d' % int(season))
		result = getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"number": season}], "ids": {"tvdb": tvdb}}]})[0]
		seasonCount(imdb)
		return result
	except:
		log_utils.error()

def markEpisodeAsWatched(imdb, tvdb, season, episode):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
	# result = getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})[0]
	result = getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})
	seasonCount(imdb)
	return result

def markEpisodeAsNotWatched(imdb, tvdb, season, episode):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
	# result = getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})[0]
	result = getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})
	seasonCount(imdb)
	return result

def getMovieTranslation(id, lang, full=False):
	url = '/movies/%s/translations/%s' % (id, lang)
	try:
		item = cache.get(getTraktAsJson, 96, url)
		if item: item = item[0]
		else: return None
		return item if full else item.get('title')
	except:
		log_utils.error()

def getTVShowTranslation(id, lang, season=None, episode=None, full=False):
	if season and episode: url = '/shows/%s/seasons/%s/episodes/%s/translations/%s' % (id, season, episode, lang)
	else: url = '/shows/%s/translations/%s' % (id, lang)
	try:
		item = cache.get(getTraktAsJson, 96, url)
		if item: item = item[0]
		else: return None
		return item if full else item.get('title')
	except:
		log_utils.error()

def getMovieSummary(id, full=True):
	try:
		url = '/movies/%s' % id
		if full: url += '?extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()

def getTVShowSummary(id, full=True):
	try:
		url = '/shows/%s' % id
		if full: url += '?extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()

def getEpisodeSummary(id, season, episode, full=True):
	try:
		url = '/shows/%s/seasons/%s/episodes/%s' % (id, season, episode)
		if full: url += '&extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()

def getSeasons(id, full=True):
	try:
		url = '/shows/%s/seasons' % (id)
		if full: url += '&extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()

def sort_list(sort_key, sort_direction, list_data):
	reverse = False if sort_direction == 'asc' else True
	if sort_key == 'rank': return sorted(list_data, key=lambda x: x['rank'], reverse=reverse)
	elif sort_key == 'added': return sorted(list_data, key=lambda x: x['listed_at'], reverse=reverse)
	elif sort_key == 'title': return sorted(list_data, key=lambda x: utils.title_key(x[x['type']].get('title')), reverse=reverse)
	elif sort_key == 'released': return sorted(list_data, key=lambda x: _released_key(x[x['type']]), reverse=reverse)
	elif sort_key == 'runtime': return sorted(list_data, key=lambda x: x[x['type']].get('runtime', 0), reverse=reverse)
	elif sort_key == 'popularity': return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
	elif sort_key == 'percentage': return sorted(list_data, key=lambda x: x[x['type']].get('rating', 0), reverse=reverse)
	elif sort_key == 'votes': return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
	else: return list_data

def _released_key(item):
	if 'released' in item: return item['released']
	elif 'first_aired' in item: return item['first_aired']
	else: return 0

def getMovieAliases(id):
	try:
		return cache.get(getTraktAsJson, 168, '/movies/%s/aliases' % id)
	except:
		log_utils.error()
		return []

def getTVShowAliases(id):
	try:
		return cache.get(getTraktAsJson, 168, '/shows/%s/aliases' % id)
	except:
		log_utils.error()
		return []

def getPeople(id, content_type, full=True):
	try:
		url = '/%s/%s/people' % (content_type, id)
		if full: url += '?extended=full'
		return cache.get(getTraktAsJson, 96, url)
	except:
		log_utils.error()

def SearchAll(title, year, full=True):
	try:
		return SearchMovie(title, year, full) + SearchTVShow(title, year, full)
	except:
		log_utils.error()
		return

def SearchMovie(title, year, fields=None, full=True):
	try:
		url = '/search/movie?query=%s' % title
		if year: url += '&year=%s' % year
		if fields: url += '&fields=%s' % fields
		if full: url += '&extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()
		return

def SearchTVShow(title, year, fields=None, full=True):
	try:
		url = '/search/show?query=%s' % title
		if year: url += '&year=%s' % year
		if fields: url += '&fields=%s' % fields
		if full: url += '&extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()
		return

def SearchEpisode(title, season, episode, full=True):
	try:
		url = '/search/%s/seasons/%s/episodes/%s' % (title, season, episode)
		if full: url += '&extended=full'
		return cache.get(getTraktAsJson, 48, url)
	except:
		log_utils.error()
		return

def getGenre(content, type, type_id):
	try:
		url = '/search/%s/%s?type=%s&extended=full' % (type, type_id, content)
		result = cache.get(getTraktAsJson, 168, url)
		if not result: return []
		return result[0].get(content, {}).get('genres', [])
	except:
		log_utils.error()
		return []

def IdLookup(id_type, id, type): # ("id_type" can be trakt , imdb , tmdb , tvdb) (type can be one of "movie , show , episode , person , list")
	try:
		url = '/search/%s/%s?type=%s' % (id_type, id, type)
		result = cache.get(getTraktAsJson, 168, url)
		if not result: return None
		return result[0].get(type).get('ids')
	except:
		log_utils.error()
		return None

def scrobbleMovie(imdb, tmdb, watched_percent):
	try:
		if not imdb.startswith('tt'): imdb = 'tt' + imdb
		timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
		items = [{'progress': watched_percent, 'paused_at': timestamp, 'type': 'movie', 'movie': {'ids': {'imdb': imdb, 'tmdb': tmdb}}}]
		traktsync.insert_bookmarks(items, new_scrobble=True)
		success = getTrakt('/scrobble/pause', {"movie": {"ids": {"imdb": imdb}}, "progress": watched_percent})
		if success:
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32088)
		else:
			control.notification(message=32130)
	except:
		log_utils.error()

def scrobbleEpisode(imdb, tmdb, tvdb, season, episode, watched_percent):
	try:
		season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
		timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
		items = [{'progress': watched_percent, 'paused_at': timestamp, 'type': 'episode', 'episode': {'season': season, 'number': episode}, 'show': {'ids': {'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb}}}]
		traktsync.insert_bookmarks(items, new_scrobble=True)
		success = getTrakt('/scrobble/pause', {"show": {"ids": {"tvdb": tvdb}}, "episode": {"season": season, "number": episode}, "progress": watched_percent})
		if success:
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32088)
		else:
			control.notification(message=32130)
	except:
		log_utils.error()

def scrobbleReset(imdb, tvdb=None, season=None, episode=None, refresh=True, widgetRefresh=False):
	control.busy()
	try:
		type = 'movie' if not episode else 'episode'
		if type == 'movie':
			items = [{'type': 'movie', 'movie': {'ids': {'imdb': imdb}}}]
			success = getTrakt('/scrobble/start', {"movie": {"ids": {"imdb": imdb}}, "progress": 0})
		else:
			items = [{'type': 'episode', 'episode': {'season': season, 'number': episode}, 'show': {'ids': {'imdb': imdb, 'tvdb': tvdb}}}]
			success = getTrakt('/scrobble/start', {"show": {"ids": {"tvdb": tvdb}}, "episode": {"season": season, "number": episode}, "progress": 0})
		timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
		items[0].update({'paused_at': timestamp})
		traktsync.delete_bookmark(items)
		control.hide()
		if refresh: control.refresh()
		if widgetRefresh:
			control.trigger_widget_refresh() # skinshortcuts handles the widget_refresh when plyback ends, but not a manual clear from Trakt Manager
		if success:
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32082)
		else:
			control.notification(message=32131)
	except:
		log_utils.error()

def sync_progress():
	try:
		while not control.monitor.abortRequested():
			db_last_paused = traktsync.last_paused_at()
			activity = getPausedActivity()
			if activity - db_last_paused >= 120: # do not sync unless 2 min difference or more
				log_utils.log('Trakt Progress Sync Update...(local db latest "paused_at" = %s, trakt api latest "paused_at" = %s)' % \
									(str(db_last_paused), str(activity)), __name__, log_utils.LOGDEBUG)
				link = '/sync/playback/'
				items = getTraktAsJson(link)
				if items: traktsync.insert_bookmarks(items)
			if control.monitor.waitForAbort(60*15): break
	except:
		log_utils.error()