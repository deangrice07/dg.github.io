# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime
from json import dumps as jsdumps, loads as jsloads
import re
from threading import Thread
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
highlight_color = control.getHighlightColor()
server_notification = control.setting('trakt.server.notifications') == 'true'

def getTrakt(url, post=None, extended=False, silent=False):
	try:
		if not url.startswith(BASE_URL): url = urljoin(BASE_URL, url)
		if post: post = jsdumps(post)
		if not getTraktCredentialsInfo():
			return client.request(url, post=post, headers=headers)

		# headers['Authorization'] = 'Bearer %s' % control.setting('trakt.token')
		headers['Authorization'] = 'Bearer %s' % control.addon('script.module.myaccounts').getSetting('trakt.token')

		result = client.request(url, post=post, headers=headers, output='extended', error=True)
		try: code = str(result[1]) # result[1] is already a str from client module
		except: code = ''

		if code.startswith('5') or (result and isinstance(result, str) and '<html' in result) or not result: # covers Maintenance html responses ["Bad Gateway", "We're sorry, but something went wrong (500)"])
			if not result: return None
			log_utils.log('Temporary Trakt Server Problems', level=log_utils.LOGINFO)
			if (not silent) and server_notification: control.notification(title=32315, message=33676)
			return None
		elif result and code in ['423']:
			log_utils.log('Locked User Account - Contact Trakt Support: %s' % str(result[0]), level=log_utils.LOGWARNING)
			if (not silent) and server_notification: control.notification(title=32315, message=33675)
			return None
		elif result and code in ['404']:
			# log_utils.log('Request Not Found: url=(%s): %s' % (url, str(result[0])), level=log_utils.LOGWARNING)
			log_utils.log('getTrakt() (404:NOT FOUND): URL=(%s): %s' % (url, str(result[0])), level=log_utils.LOGWARNING)
			return None # change to (return '404:NOT FOUND') to cache only 404's but not server response failures
		elif result and code in ['429']:
			if 'Retry-After' in result[2]: # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME (1000 calls every 5 minutes, doubt we'll ever hit that)
				throttleTime = result[2]['Retry-After']
				if (not silent) and server_notification: control.notification(title=32315, message='Trakt Throttling Applied, Sleeping for %s seconds' % throttleTime) # message lang code 33674
				control.sleep((int(throttleTime) + 1) * 1000)
				return getTrakt(url, post=post, extended=extended, silent=silent)
		elif result and code in ['401']: # Re-Auth token
			success = re_auth(headers)
			if success: return getTrakt(url, post=post, extended=extended, silent=silent)
		if result and code not in ['401', '405']:
			if extended: return result[0], result[2]
			else: return result[0]
	except:
		log_utils.error('getTrakt Error: ')
	return None

def getTraktAsJson(url, post=None, silent=False):
	try:
		res_headers = {}
		r = getTrakt(url=url, post=post, extended=True, silent=silent)
		if isinstance(r, tuple) and len(r) == 2:
			r, res_headers = r[0], r[1]
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
			control.setSetting('trakt.isauthed', 'true')
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
	if (username == '' or token == '' or refresh == ''): return False
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

def like_list(list_owner, list_name, list_id):
	try:
		headers['Authorization'] = 'Bearer %s' % control.addon('script.module.myaccounts').getSetting('trakt.token')
		resp_code = client._basic_request('https://api.trakt.tv/users/%s/lists/%s/like' % (list_owner, list_id), headers=headers, method='POST', ret_code=True)
		if resp_code == 204:
			control.notification(title=32315, message='Successfuly Liked list:  [COLOR %s]%s[/COLOR]' % (highlight_color, list_name))
			sync_liked_lists()
		else: control.notification(title=32315, message='Failed to Like list %s' % list_name)
		control.refresh()
	except:
		log_utils.error()

def unlike_list(list_owner, list_name, list_id):
	try:
		headers['Authorization'] = 'Bearer %s' % control.addon('script.module.myaccounts').getSetting('trakt.token')
		resp_code = client._basic_request('https://api.trakt.tv/users/%s/lists/%s/like' % (list_owner, list_id), headers=headers, method='DELETE', ret_code=True)
		if resp_code == 204:
			control.notification(title=32315, message='Successfuly Unliked list:  [COLOR %s]%s[/COLOR]' % (highlight_color, list_name))
			traktsync.delete_liked_list(list_id)
		else: control.notification(title=32315, message='Failed to UnLike list %s' % list_name)
		control.refresh()
	except:
		log_utils.error()

def remove_liked_lists(trakt_ids):
	if not trakt_ids: return
	success = None
	try:
		headers['Authorization'] = 'Bearer %s' % control.addon('script.module.myaccounts').getSetting('trakt.token')
		for id in trakt_ids:
			list_owner = id.get('list_owner')
			list_id = id.get('trakt_id')
			list_name = id.get('list_name')
			resp_code = client._basic_request('https://api.trakt.tv/users/%s/lists/%s/like' % (list_owner, list_id), headers=headers, method='DELETE', ret_code=True)
			if resp_code == 204:
				control.notification(title=32315, message='Successfuly Unliked list:  [COLOR %s]%s[/COLOR]' % (highlight_color, list_name))
				traktsync.delete_liked_list(list_id)
			else: control.notification(title=32315, message='Failed to UnLike list %s' % list_name)
			control.sleep(1000)
		control.refresh()
	except:
		log_utils.error()

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
			import importlib.util
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

			script_path = control.joinPath(control.addonPath(addon), 'resources', 'lib', 'sqlitequeue.py')
			spec = importlib.util.spec_from_file_location("sqlitequeue.py", script_path)
			sqlitequeue = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(sqlitequeue)
			data = {'action': 'manualRating', 'ratingData': data}
			sqlitequeue.SqliteQueue().append(data)
		else:
			control.notification(title=32315, message=33659)
		control.hide()
	except:
		log_utils.error()

def unHideItems(tvdb_ids):
	if not tvdb_ids: return
	success = None
	try:
		sections = ['progress_watched', 'calendar']
		ids = []
		for id in tvdb_ids: ids.append({"ids": {"tvdb": int(id)}})
		post = {"shows": ids}
		for section in sections:
			success = getTrakt('users/hidden/%s/remove' % section, post=post)
			control.sleep(1000)
		if success:
			if 'plugin.video.dg' in control.infoLabel('Container.PluginName'): control.refresh()
			traktsync.delete_hidden_progress(tvdb_ids)
			control.trigger_widget_refresh()
			return True
	except:
		log_utils.error()
		return False

def hideItems(tvdb_ids):
	if not tvdb_ids: return
	success = None
	try:
		sections = ['progress_watched', 'calendar']
		ids = []
		for id in tvdb_ids: ids.append({"ids": {"tvdb": int(id)}})
		post = {"shows": ids}
		for section in sections:
			success =getTrakt('users/hidden/%s' % section, post=post)
			control.sleep(1000)
		if success:
			if 'plugin.video.dg' in control.infoLabel('Container.PluginName'): control.refresh()
			sync_hidden_progress(forced=True)
			control.trigger_widget_refresh()
			return True
	except:
		log_utils.error()
		return False

def hideItem(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True):
	success = None
	try:
		sections = ['progress_watched', 'calendar']
		sections_display = [control.lang(40072), control.lang(40073), control.lang(32181)]
		selection = control.selectDialog([i for i in sections_display], heading=control.addonInfo('name') + ' - ' + control.lang(40074))
		if selection == -1: return
		control.busy()
		if episode: post = {"shows": [{"ids": {"tvdb": tvdb}}]}
		else: post = {"movies": [{"ids": {"imdb": imdb}}]}
		if selection in [0, 1]:
			section = sections[selection]
			success = getTrakt('users/hidden/%s' % section, post=post)
		else:
			for section in sections:
				success = getTrakt('users/hidden/%s' % section, post=post)
				control.sleep(1000)
		if success:
			control.hide()
			sync_hidden_progress(forced=True)
			if refresh: control.refresh()
			control.trigger_widget_refresh()
			if control.setting('trakt.general.notifications') == 'true':
				control.notification(title=32315, message=control.lang(33053) % (name, sections_display[selection]))
	except:
		log_utils.error()

def removeCollectionItems(type, id_list):
	if not id_list: return
	success = None
	try:
		ids = []
		total_items = len(id_list)
		for id in id_list: ids.append({"ids": {"trakt": id}})
		post = {type: ids}
		success =getTrakt('/sync/collection/remove', post=post)
		if success:
			# if 'plugin.video.dg' in control.infoLabel('Container.PluginName'): control.refresh()
			control.trigger_widget_refresh()
			if type == 'movies': traktsync.delete_collection_items(id_list, 'movies_collection')
			else: traktsync.delete_collection_items(id_list, 'shows_collection')
			if control.setting('trakt.general.notifications') == 'true':
				control.notification(title='Trakt Collection Manager', message='Successfuly Removed %s Item%s' % (total_items, 's' if total_items >1 else ''))
	except:
		log_utils.error()

def removeWatchlistItems(type, id_list):
	if not id_list: return
	success = None
	try:
		ids = []
		total_items = len(id_list)
		for id in id_list: ids.append({"ids": {"trakt": id}})
		post = {type: ids}
		success =getTrakt('/sync/watchlist/remove', post=post)
		if success:
			# if 'plugin.video.dg' in control.infoLabel('Container.PluginName'): control.refresh()
			control.trigger_widget_refresh()
			if type == 'movies': traktsync.delete_watchList_items(id_list, 'movies_watchlist')
			else: traktsync.delete_watchList_items(id_list, 'shows_watchlist')
			if control.setting('trakt.general.notifications') == 'true':
				control.notification(title='Trakt Watch List Manager', message='Successfuly Removed %s Item%s' % (total_items, 's' if total_items >1 else ''))
	except:
		log_utils.error()

def manager(name, imdb=None, tvdb=None, season=None, episode=None, refresh=True, watched=None, unfinished=False):
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
		if tvdb:
			items += [(control.lang(40075) % (highlight_color, media_type), 'hideItem')]
			items += [(control.lang(35058) % highlight_color, 'hiddenManager')]
		if unfinished is True:
			if media_type == 'Movie': items += [(control.lang(35059) % highlight_color, 'unfinishedMovieManager')]
			elif episode: items += [(control.lang(35060) % highlight_color, 'unfinishedEpisodeManager')]
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
			elif items[select][1] == 'hiddenManager':
				control.execute('RunPlugin(plugin://plugin.video.dg/?action=shows_traktHiddenManager)')
			elif items[select][1] == 'unfinishedEpisodeManager':
				control.execute('RunPlugin(plugin://plugin.video.dg/?action=episodes_traktUnfinishedManager)')
			elif items[select][1] == 'unfinishedMovieManager':
				control.execute('RunPlugin(plugin://plugin.video.dg/?action=movies_traktUnfinishedManager)')
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
					if slug: getTrakt(items[select][1] % slug, post=post)
				else:
					getTrakt(items[select][1], post=post)

				if items[select][1] == '/sync/watchlist':
					sync_watch_list(forced=True)
				if items[select][1] == '/sync/watchlist/remove':
					if media_type == 'Movie':
						traktsync.delete_watchList_items([imdb], 'movies_watchlist', 'imdb')
					else:
						traktsync.delete_watchList_items([tvdb], 'shows_watchlist', 'tvdb')
				if items[select][1] == '/sync/collection':
					sync_collection(forced=True)
				if items[select][1] == '/sync/collection/remove':
					if media_type == 'Movie':
						traktsync.delete_collection_items([imdb], 'movies_collection', 'imdb')
					else:
						traktsync.delete_collection_items([tvdb], 'shows_collection', 'tvdb')

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

def getHiddenActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['hidden_at'])
		activity.append(i['shows']['hidden_at'])
		activity.append(i['seasons']['hidden_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getWatchedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watched_at'])
		activity.append(i['episodes']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getMoviesWatchedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getEpisodesWatchedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['episodes']['watched_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getCollectedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['collected_at'])
		activity.append(i['episodes']['collected_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getWatchListedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
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

def getPausedActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['movies']['paused_at'])
		activity.append(i['episodes']['paused_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getListActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['lists']['liked_at'])
		activity.append(i['lists']['updated_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getUserListActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['lists']['updated_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def getProgressActivity(activities=None):
	try:
		if activities: i = activities
		else: i = getTraktAsJson('/sync/last_activities')
		if not i: return 0
		activity = []
		activity.append(i['episodes']['watched_at'])
		activity.append(i['shows']['hidden_at'])
		activity.append(i['seasons']['hidden_at'])
		activity = [int(cleandate.iso_2_utc(i)) for i in activity]
		activity = sorted(activity, key=int)[-1]
		return activity
	except:
		log_utils.error()

def cachesyncMovies(timeout=0):
	indicators = cache.get(syncMovies, timeout)
	return indicators

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
	threads = [Thread(target=cachesyncTVShows), Thread(target=cachesyncSeason, args=(imdb,))]
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
			thread = Thread(target=_seasonCountCache, args=(imdb,))
			thread.start()
			if wait: # Do not wait to retrieve a fresh count, otherwise loading show/season menus are slow.
				thread.join()
				indicators = cache.cache_existing(_seasonCountRetrieve, imdb)
		return indicators
	except:
		log_utils.error()
		return None

def _seasonCountCache(imdb):
	# return cache.get(_seasonCountRetrieve, 0.3, imdb) # this may be causing manual marking as watched/unwatched to not update season counts
	return cache.get(_seasonCountRetrieve, 0, imdb)

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
	return getTrakt('/sync/history', {"movies": [{"ids": {"imdb": imdb}}]})

def markMovieAsNotWatched(imdb):
	if not imdb.startswith('tt'): imdb = 'tt' + imdb
	return getTrakt('/sync/history/remove', {"movies": [{"ids": {"imdb": imdb}}]})

def markTVShowAsWatched(imdb, tvdb):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	result = getTrakt('/sync/history', {"shows": [{"ids": {"tvdb": tvdb}}]})
	seasonCount(imdb)
	return result

def markTVShowAsNotWatched(imdb, tvdb):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	result = getTrakt('/sync/history/remove', {"shows": [{"ids": {"tvdb": tvdb}}]})
	seasonCount(imdb)
	return result

def markSeasonAsWatched(imdb, tvdb, season):
	try:
		if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
		season = int('%01d' % int(season))
		result = getTrakt('/sync/history', {"shows": [{"seasons": [{"number": season}], "ids": {"tvdb": tvdb}}]})
		seasonCount(imdb)
		return result
	except:
		log_utils.error()

def markSeasonAsNotWatched(imdb, tvdb, season):
	try:
		if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
		season = int('%01d' % int(season))
		result = getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"number": season}], "ids": {"tvdb": tvdb}}]})
		seasonCount(imdb)
		return result
	except:
		log_utils.error()

def markEpisodeAsWatched(imdb, tvdb, season, episode):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
	result = getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})
	seasonCount(imdb)
	return result

def markEpisodeAsNotWatched(imdb, tvdb, season, episode):
	if imdb and not imdb.startswith('tt'): imdb = 'tt' + imdb
	season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
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
	try:
		reverse = False if sort_direction == 'asc' else True
		if sort_key == 'rank': return sorted(list_data, key=lambda x: x['rank'], reverse=reverse)
		elif sort_key == 'added': return sorted(list_data, key=lambda x: x['listed_at'], reverse=reverse)
		elif sort_key == 'title': return sorted(list_data, key=lambda x: _title_key(x[x['type']].get('title')), reverse=reverse)
		elif sort_key == 'released': return sorted(list_data, key=lambda x: _released_key(x[x['type']]), reverse=reverse)
		elif sort_key == 'runtime': return sorted(list_data, key=lambda x: x[x['type']].get('runtime', 0), reverse=reverse)
		elif sort_key == 'popularity': return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
		elif sort_key == 'percentage': return sorted(list_data, key=lambda x: x[x['type']].get('rating', 0), reverse=reverse)
		elif sort_key == 'votes': return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
		else: return list_data
	except:
		log_utils.error()

def _title_key(title):
	try:
		if not title: title = ''
		articles_en = ['the', 'a', 'an']
		articles_de = ['der', 'die', 'das']
		articles = articles_en + articles_de
		match = re.match(r'^((\w+)\s+)', title.lower())
		if match and match.group(2) in articles: offset = len(match.group(1))
		else: offset = 0
		return title[offset:]
	except:
		return title

def _released_key(item):
	try:
		if 'released' in item: return item['released'] or '0'
		elif 'first_aired' in item: return item['first_aired'] or '0'
		else: return '0'
	except:
		log_utils.error()

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

def IdLookup(id_type, id, type): # ("id_type" can be trakt, imdb, tmdb, tvdb) (type can be one of "movie , show , episode , person , list")
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
		success = getTrakt('/scrobble/pause', {"movie": {"ids": {"imdb": imdb}}, "progress": watched_percent})
		if success:
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32088)
			control.sleep(1000)
			sync_playbackProgress(forced=True)
		else:
			control.notification(message=32130)
	except:
		log_utils.error()

def scrobbleEpisode(imdb, tmdb, tvdb, season, episode, watched_percent):
	try:
		season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
		success = getTrakt('/scrobble/pause', {"show": {"ids": {"tvdb": tvdb}}, "episode": {"season": season, "number": episode}, "progress": watched_percent})
		if success:
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32088)
			control.sleep(1000)
			sync_playbackProgress(forced=True)
		else:
			control.notification(message=32130)
	except:
		log_utils.error()

def scrobbleReset(imdb, tvdb=None, season=None, episode=None, refresh=True, widgetRefresh=False):
	if not getTraktCredentialsInfo(): return
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
		if success:
			if refresh: control.refresh()
			if widgetRefresh: control.trigger_widget_refresh() # skinshortcuts handles the widget_refresh when plyback ends, but not a manual clear from Trakt Manager
			if control.setting('trakt.scrobble.notify') == 'true': control.notification(message=32082)
		else: control.notification(message=32131)
	except:
		log_utils.error()

def scrobbleResetItems(imdb_ids, tvdb_dicts=None, refresh=True, widgetRefresh=False):
	control.busy()
	try:
		type = 'movie' if not tvdb_dicts else 'episode'
		if type == 'movie':
			total_items = len(imdb_ids)
			for imdb in imdb_ids:
				success = getTrakt('/scrobble/start', {"movie": {"ids": {"imdb": imdb}}, "progress": 0})
				items = [{'type': 'movie', 'movie': {'ids': {'imdb': imdb}}}]
				timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
				items[0].update({'paused_at': timestamp})
				traktsync.delete_bookmark(items)
				control.sleep(1000)
		else:
			total_items = len(tvdb_dicts)
			for dict in tvdb_dicts:
				imdb = dict.get('imdb')
				tvdb = dict.get('tvdb')
				season = dict.get('season')
				episode = dict.get('episode')
				items = [{'type': 'episode', 'episode': {'season': season, 'number': episode}, 'show': {'ids': {'imdb': imdb, 'tvdb': tvdb}}}]
				success = getTrakt('/scrobble/start', {"show": {"ids": {"tvdb": tvdb}}, "episode": {"season": season, "number": episode}, "progress": 0})
				timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
				items[0].update({'paused_at': timestamp})
				traktsync.delete_bookmark(items)
				control.sleep(1000)
		control.hide()
		if success:
			if refresh: control.refresh()
			if widgetRefresh: control.trigger_widget_refresh() # skinshortcuts handles the widget_refresh when plyback ends, but not a manual clear from Trakt Manager
			control.notification(title='Trakt Playback Progress Manager', message='Successfuly Removed %s Item%s' % (total_items, 's' if total_items >1 else ''))
			return True
		else: return False
	except:
		log_utils.error()
		return False


#############    SERVICE SYNC    ######################
def trakt_service_sync():
	while not control.monitor.abortRequested():
		if getTraktCredentialsInfo: # run service in case user auth's trakt later
			activities = getTraktAsJson('/sync/last_activities', silent=True)
			if control.setting('bookmarks') == 'true' and control.setting('resume.source') == '1':
				sync_playbackProgress(activities)
			sync_watchedProgress(activities)
			if control.setting('indicators.alt') == '1':
				sync_watched(activities) # still writes to cache.db
			sync_user_lists(activities)
			sync_liked_lists(activities)
			sync_hidden_progress(activities)
			sync_collection(activities)
			sync_watch_list(activities)
			sync_popular_lists()
			sync_trending_lists()
		if control.monitor.waitForAbort(60*15): break

def force_traktSync():
	if not control.yesnoDialog(control.lang(32056), '', ''): return
	control.busy()
	sync_playbackProgress(forced=True)
	sync_watchedProgress(forced=True)
	sync_watched(forced=True) # still writes to cache.db
	sync_user_lists(forced=True)
	sync_liked_lists(forced=True)
	sync_hidden_progress(forced=True)
	sync_collection(forced=True)
	sync_watch_list(forced=True)
	sync_popular_lists(forced=True)
	sync_trending_lists(forced=True)
	control.hide()
	control.notification(message='Forced Trakt Sync Complete')

def sync_playbackProgress(activities=None, forced=False):
	try:
		link = '/sync/playback/?extended=full'
		if forced:
			items = getTraktAsJson(link, silent=True)
			if items: traktsync.insert_bookmarks(items)
		else:
			db_last_paused = traktsync.last_sync('last_paused_at')
			activity = getPausedActivity(activities)
			if activity - db_last_paused >= 120: # do not sync unless 2 min difference or more
				log_utils.log('Trakt Playback Progress Sync Update...(local db latest "paused_at" = %s, trakt api latest "paused_at" = %s)' % \
									(str(db_last_paused), str(activity)), __name__, log_utils.LOGDEBUG)
				items = getTraktAsJson(link, silent=True)
				if items: traktsync.insert_bookmarks(items)
	except:
		log_utils.error()

def sync_watchedProgress(activities=None, forced=False):
	try:
		from resources.lib.menus import episodes
		trakt_user = control.setting('trakt.username').strip()
		lang = control.apiLanguage()['tmdb']
		direct = control.setting('trakt.directProgress.scrape') == 'true'
		url = 'https://api.trakt.tv/users/me/watched/shows'
		if forced or (getProgressActivity(activities) > cache.timeout(episodes.Episodes().trakt_progress_list, url, trakt_user, lang, direct)):
			cache.get(episodes.Episodes().trakt_progress_list, 0, url, trakt_user, lang, direct)
		else: cache.get(episodes.Episodes().trakt_progress_list, 3, url, trakt_user, lang, direct)
	except:
		log_utils.error()

def sync_watched(activities=None, forced=False): # still writes to cache.db, move to traktsync.db
	try:
		if forced:
			cachesyncMovies()
			cachesyncTVShows()
		else:
			moviesWatchedActivity = getMoviesWatchedActivity(activities)
			db_movies_last_watched = timeoutsyncMovies()
			episodesWatchedActivity = getEpisodesWatchedActivity(activities)
			db_episoodes_last_watched = timeoutsyncTVShows()
			if moviesWatchedActivity > db_movies_last_watched:
				log_utils.log('Trakt Watched Movie Sync Update...(local db latest "watched_at" = %s, trakt api latest "watched_at" = %s)' % \
								(str(db_movies_last_watched), str(moviesWatchedActivity)), __name__, log_utils.LOGDEBUG)
				cachesyncMovies()
			if episodesWatchedActivity > db_episoodes_last_watched:
				log_utils.log('Trakt Watched Episodes Sync Update...(local db latest "watched_at" = %s, trakt api latest "watched_at" = %s)' % \
								(str(db_episoodes_last_watched), str(episodesWatchedActivity)), __name__, log_utils.LOGDEBUG)
				cachesyncTVShows()
	except:
		log_utils.error()

def sync_user_lists(activities=None, forced=False):
	try:
		link = '/users/me/lists'
		list_link = '/users/me/lists/%s/items/%s'
		if forced:
			items = getTraktAsJson(link, silent=True)
			for i in items:
				i['content_type'] = ''
				trakt_id = i['ids']['trakt']
				list_items = getTraktAsJson(list_link % (trakt_id, 'movies'), silent=True)
				if not list_items or list_items == '[]': pass
				else: i['content_type'] = 'movies'
				list_items = getTraktAsJson(list_link % (trakt_id, 'shows'), silent=True)
				if not list_items or list_items == '[]': pass
				else: i['content_type'] = 'mixed' if i['content_type'] == 'movies' else 'shows'
				control.sleep(200)
			traktsync.insert_user_lists(items)
		else:
			db_last_lists_updatedat = traktsync.last_sync('last_lists_updatedat')
			user_listActivity = getUserListActivity(activities)
			if user_listActivity > db_last_lists_updatedat:
				log_utils.log('Trakt User Lists Sync Update...(local db latest "lists_updatedat" = %s, trakt api latest "lists_updatedat" = %s)' % \
									(str(db_last_lists_updatedat), str(user_listActivity)), __name__, log_utils.LOGDEBUG)
				items = getTraktAsJson(link, silent=True)
				for i in items:
					i['content_type'] = ''
					trakt_id = i['ids']['trakt']
					list_items = getTraktAsJson(list_link % (trakt_id, 'movies'), silent=True)
					if not list_items or list_items == '[]': pass
					else: i['content_type'] = 'movies'
					list_items = getTraktAsJson(list_link % (trakt_id, 'shows'), silent=True)
					if not list_items or list_items == '[]': pass
					else: i['content_type'] = 'mixed' if i['content_type'] == 'movies' else 'shows'
					control.sleep(200)
				traktsync.insert_user_lists(items)
	except:
		log_utils.error()

def sync_liked_lists(activities=None, forced=False):
	try:
		link = '/users/likes/lists?limit=1000000'
		list_link = '/users/%s/lists/%s/items/%s'
		db_last_liked = traktsync.last_sync('last_liked_at')
		listActivity = getListActivity(activities)
		if (listActivity > db_last_liked) or forced:
			log_utils.log('Trakt Liked Lists Sync Update...(local db latest "liked_at" = %s, trakt api latest "liked_at" = %s)' % \
								(str(db_last_liked), str(listActivity)), __name__, log_utils.LOGDEBUG)
			items = getTraktAsJson(link, silent=True)
			thrd_items = []
			def items_list(i):
				list_item = i.get('list', {})
				if any(list_item.get('privacy', '') == value for value in ['private', 'friends']): return
				i['list']['content_type'] = ''
				list_owner_slug = list_item.get('user', {}).get('ids', {}).get('slug', '')
				trakt_id = list_item.get('ids', {}).get('trakt', '')
				list_items = getTraktAsJson(list_link % (list_owner_slug, trakt_id, 'movies'), silent=True)
				if not list_items or list_items == '[]': pass
				else: i['list']['content_type'] = 'movies'
				list_items = getTraktAsJson(list_link % (list_owner_slug, trakt_id, 'shows'), silent=True)
				if not list_items or list_items == '[]': pass
				else: i['list']['content_type'] = 'mixed' if i['list']['content_type'] == 'movies' else 'shows'
				thrd_items.append(i)
			threads = []
			for i in items:
				threads.append(Thread(target=items_list, args=(i,)))
			[i.start() for i in threads]
			[i.join() for i in threads]
			traktsync.insert_liked_lists(thrd_items)
	except:
		log_utils.error()

def sync_hidden_progress(activities=None, forced=False):
	try:
		link = '/users/hidden/progress_watched?limit=1000&type=show'
		if forced:
			items = getTraktAsJson(link, silent=True)
			traktsync.insert_hidden_progress(items)
		else:
			db_last_hidden = traktsync.last_sync('last_hiddenProgress_at')
			hiddenActivity = getHiddenActivity(activities)
			if hiddenActivity > db_last_hidden:
				log_utils.log('Trakt Hidden Progress Sync Update...(local db latest "hidden_at" = %s, trakt api latest "hidden_at" = %s)' % \
									(str(db_last_hidden), str(hiddenActivity)), __name__, log_utils.LOGDEBUG)
				items = getTraktAsJson(link, silent=True)
				traktsync.insert_hidden_progress(items)
	except:
		log_utils.error()

def sync_collection(activities=None, forced=False):
	try:
		link = '/users/me/collection/%s?extended=full'
		if forced:
			items = getTraktAsJson(link % 'movies', silent=True)
			traktsync.insert_collection(items, 'movies_collection')
			items = getTraktAsJson(link % 'shows', silent=True)
			traktsync.insert_collection(items, 'shows_collection')
		else:
			db_last_collected = traktsync.last_sync('last_collected_at')
			collectedActivity = getCollectedActivity(activities)
			if collectedActivity > db_last_collected:
				log_utils.log('Trakt Collection Sync Update...(local db latest "collected_at" = %s, trakt api latest "collected_at" = %s)' % \
									(str(db_last_collected), str(collectedActivity)), __name__, log_utils.LOGDEBUG)
				# indicators = cachesyncMovies() # could maybe check watched status here to satisfy sort method
				items = getTraktAsJson(link % 'movies', silent=True)
				traktsync.insert_collection(items, 'movies_collection')
				# indicators = cachesyncTVShows() # could maybe check watched status here to satisfy sort method
				items = getTraktAsJson(link % 'shows', silent=True)
				traktsync.insert_collection(items, 'shows_collection')
	except:
		log_utils.error()

def sync_watch_list(activities=None, forced=False):
	try:
		link = '/users/me/watchlist/%s?extended=full'
		if forced:
			items = getTraktAsJson(link % 'movies', silent=True)
			traktsync.insert_watch_list(items, 'movies_watchlist')
			items = getTraktAsJson(link % 'shows', silent=True)
			traktsync.insert_watch_list(items, 'shows_watchlist')
		else:
			db_last_watchList = traktsync.last_sync('last_watchlisted_at')
			watchListActivity = getWatchListedActivity(activities)
			if watchListActivity > db_last_watchList:
				log_utils.log('Trakt Watch List Sync Update...(local db latest "watchlist_at" = %s, trakt api latest "watchlisted_at" = %s)' % \
									(str(db_last_watchList), str(watchListActivity)), __name__, log_utils.LOGDEBUG)
				items = getTraktAsJson(link % 'movies', silent=True)
				traktsync.insert_watch_list(items, 'movies_watchlist')
				items = getTraktAsJson(link % 'shows', silent=True)
				traktsync.insert_watch_list(items, 'shows_watchlist')
	except:
		log_utils.error()

def sync_popular_lists(forced=False):
	try:
		from datetime import timedelta
		link = '/lists/popular?limit=300'
		list_link = '/users/%s/lists/%s/items/movie,show'
		db_last_popularList = traktsync.last_sync('last_popularlist_at')
		cache_expiry = (datetime.utcnow() - timedelta(hours=168)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
		cache_expiry = int(cleandate.iso_2_utc(cache_expiry))
		if (cache_expiry > db_last_popularList) or forced:
			log_utils.log('Trakt Popular Lists Sync Update...(local db latest "popularlist_at" = %s, cache expiry = %s)' % \
								(str(db_last_popularList), str(cache_expiry)), __name__, log_utils.LOGDEBUG)
			items = getTraktAsJson(link, silent=True)
			thrd_items = []
			def items_list(i):
				list_item = i.get('list', {})
				if any(list_item.get('privacy', '') == value for value in ['private', 'friends']): return
				trakt_id = list_item.get('ids', {}).get('trakt', '')
				exists = traktsync.fetch_public_list(trakt_id)
				if exists:
					local = int(cleandate.iso_2_utc(exists.get('updated_at', '')))
					remote = int(cleandate.iso_2_utc(list_item.get('updated_at', '')))
					if remote > local: pass
					else: return
				i['list']['content_type'] = ''
				list_owner_slug = list_item.get('user', {}).get('ids', {}).get('slug', '')
				list_items = getTraktAsJson(list_link % (list_owner_slug, trakt_id), silent=True)
				if not list_items: return
				movie_items = [x for x in list_items if x.get('type', '') == 'movie']
				if len(movie_items) > 0: i['list']['content_type'] = 'movies'
				shows_items = [x for x in list_items if x.get('type', '') == 'show']
				if len(shows_items) > 0:
					i['list']['content_type'] = 'mixed' if i['list']['content_type'] == 'movies' else 'shows'
				thrd_items.append(i)
			threads = []
			for i in items:
				threads.append(Thread(target=items_list, args=(i,)))
			[i.start() for i in threads]
			[i.join() for i in threads]
			traktsync.insert_public_lists(thrd_items, service_type='last_popularlist_at', new_sync=False)
	except:
		log_utils.error()

def sync_trending_lists(forced=False):
	try:
		from datetime import timedelta
		link = '/lists/trending?limit=300'
		list_link = '/users/%s/lists/%s/items/movie,show'
		db_last_trendingList = traktsync.last_sync('last_trendinglist_at')
		cache_expiry = (datetime.utcnow() - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
		cache_expiry = int(cleandate.iso_2_utc(cache_expiry))
		if (cache_expiry > db_last_trendingList) or forced:
			log_utils.log('Trakt Trending Lists Sync Update...(local db latest "trendinglist_at" = %s, cache expiry = %s)' % \
								(str(db_last_trendingList), str(cache_expiry)), __name__, log_utils.LOGDEBUG)
			items = getTraktAsJson(link, silent=True)
			thrd_items = []
			def items_list(i):
				list_item = i.get('list', {})
				if any(list_item.get('privacy', '') == value for value in ['private', 'friends']): return
				trakt_id = list_item.get('ids', {}).get('trakt', '')
				exists = traktsync.fetch_public_list(trakt_id)
				if exists:
					local = int(cleandate.iso_2_utc(exists.get('updated_at', '')))
					remote = int(cleandate.iso_2_utc(list_item.get('updated_at', '')))
					if remote > local: pass
					else: return
				i['list']['content_type'] = ''
				list_owner_slug = list_item.get('user', {}).get('ids', {}).get('slug', '')
				list_items = getTraktAsJson(list_link % (list_owner_slug, trakt_id), silent=True)
				if not list_items: return
				movie_items = [x for x in list_items if x.get('type', '') == 'movie']
				if len(movie_items) != 0: i['list']['content_type'] = 'movies'
				shows_items = [x for x in list_items if x.get('type', '') == 'show']
				if len(shows_items) != 0:
					i['list']['content_type'] = 'mixed' if i['list']['content_type'] == 'movies' else 'shows'
				thrd_items.append(i)
			threads = []
			for i in items:
				threads.append(Thread(target=items_list, args=(i,)))
			[i.start() for i in threads]
			[i.join() for i in threads]
			traktsync.insert_public_lists(thrd_items, service_type='last_trendinglist_at', new_sync=False)
	except:
		log_utils.error()