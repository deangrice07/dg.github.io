# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from resources.lib.modules.control import setting as getSetting

def debrid_resolvers(order_matters=True):
	try:
		ad_enabled = getSetting('alldebrid.token') != '' and getSetting('alldebrid.enable') == 'true'
		pm_enabled = getSetting('premiumize.token') != '' and getSetting('premiumize.enable') == 'true'
		rd_enabled = getSetting('realdebrid.token') != '' and getSetting('realdebrid.enable') == 'true'
		premium_resolvers = []
		if ad_enabled:
			from resources.lib.debrid import alldebrid
			premium_resolvers.append(alldebrid.AllDebrid())
		if pm_enabled:
			from resources.lib.debrid import premiumize
			premium_resolvers.append(premiumize.Premiumize())
		if rd_enabled:
			from resources.lib.debrid import realdebrid
			premium_resolvers.append(realdebrid.RealDebrid())
		if order_matters:
			premium_resolvers.sort(key=lambda x: get_priority(x))
		return premium_resolvers
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def status():
	return debrid_resolvers() != []

def get_priority(cls):
	try:
		return int(getSetting((cls.__class__.__name__ + '.priority').lower()))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return 10