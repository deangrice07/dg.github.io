# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import myaccounts
from resources.lib.modules.control import setting as getSetting, setSetting, notification


def syncMyAccounts(silent=False):
	try:
		all_acct = myaccounts.getAll()
		trakt_acct = all_acct.get('trakt')
		if getSetting('trakt.token') != trakt_acct.get('token'):
			setSetting('trakt.isauthed', 'true')
			setSetting('trakt.token', trakt_acct.get('token'))
			setSetting('trakt.username', trakt_acct.get('username'))
			setSetting('trakt.refresh', trakt_acct.get('refresh'))
			setSetting('trakt.expires', trakt_acct.get('expires'))

		ad_acct = all_acct.get('alldebrid')
		if getSetting('alldebrid.username') != ad_acct.get('username'):
			setSetting('alldebrid.token', ad_acct.get('token'))
			setSetting('alldebrid.username', ad_acct.get('username'))

		pm_acct = all_acct.get('premiumize')
		if getSetting('premiumize.username') != pm_acct.get('username'):
			setSetting('premiumize.token', pm_acct.get('token'))
			setSetting('premiumize.username', pm_acct.get('username'))

		rd_acct = all_acct.get('realdebrid') # token refresh 1hr expiry, Venom handles this internally
		if getSetting('realdebrid.username') != rd_acct.get('username'):
			setSetting('realdebrid.token', rd_acct.get('token'))
			setSetting('realdebrid.username', rd_acct.get('username'))
			setSetting('realdebrid.client_id', rd_acct.get('client_id'))
			setSetting('realdebrid.refresh', rd_acct.get('refresh'))
			setSetting('realdebrid.secret', rd_acct.get('secret'))

		fanart_acct = all_acct.get('fanart_tv')
		if getSetting('fanart.tv.api.key') != fanart_acct.get('api_key'):
			setSetting('fanart.tv.api.key', fanart_acct.get('api_key'))

		tmdb_acct = all_acct.get('tmdb')
		if getSetting('tmdb.api.key') != tmdb_acct.get('api_key'):
			setSetting('tmdb.api.key', tmdb_acct.get('api_key'))
		if getSetting('tmdb.username') != tmdb_acct.get('username'):
			setSetting('tmdb.username', tmdb_acct.get('username'))
		if getSetting('tmdb.password') != tmdb_acct.get('password'):
			setSetting('tmdb.password', tmdb_acct.get('password'))
		if getSetting('tmdb.session_id') != tmdb_acct.get('session_id'):
			setSetting('tmdb.session_id', tmdb_acct.get('session_id'))

		tvdb_acct = all_acct.get('tvdb')
		if getSetting('tvdb.api.key') != tvdb_acct.get('api_key'):
			setSetting('tvdb.api.key', tvdb_acct.get('api_key'))

		imdb_acct = all_acct.get('imdb')
		if getSetting('imdb.user') != imdb_acct.get('user'):
			setSetting('imdb.user', imdb_acct.get('user'))

		fu_acct = all_acct.get('furk')
		if getSetting('furk.username') != fu_acct.get('username'):
			setSetting('furk.username', fu_acct.get('username'))
			setSetting('furk.password', fu_acct.get('password'))
		if fu_acct.get('api_key', None):
			if getSetting('furk.api') != fu_acct.get('api_key'):
				setSetting('furk.api', fu_acct.get('api_key'))
		if not silent: notification(message=32114)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()