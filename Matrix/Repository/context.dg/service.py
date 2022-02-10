# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui

properties = [
	'context.dg.settings',
	'context.dg.traktManager',
	'context.dg.clearProviders',
	'context.dg.clearBookmark',
	'context.dg.rescrape',
	'context.dg.playFromHere',
	'context.dg.autoPlay',
	'context.dg.sourceSelect',
	'context.dg.findSimilar',
	'context.dg.browseSeries',
	'context.dg.browseEpisodes',]

def getKodiVersion():
	return int(xbmc.getInfoLabel("System.BuildVersion")[:2])
LOGNOTICE = xbmc.LOGNOTICE if getKodiVersion() < 19 else xbmc.LOGINFO # (2 in 18, deprecated in 19 use LOGINFO(1))


class PropertiesUpdater(xbmc.Monitor):
	def __init__(self):
		for id in properties:
			if xbmcaddon.Addon().getSetting(id) == 'true':
				xbmc.executebuiltin('SetProperty({0},true,home)'.format(id))
				xbmc.log('[ context.dg ]  menu item enabled: {0}'.format(id), LOGNOTICE)

	def onSettingsChanged(self):
		for id in properties:
			if xbmcaddon.Addon().getSetting(id) == 'true':
				xbmc.executebuiltin('SetProperty({0},true,home)'.format(id))
				xbmc.log('[ context.dg ]  menu item enabled: {0}'.format(id), LOGNOTICE)
			else:
				xbmc.executebuiltin('ClearProperty({0},home)'.format(id))
				xbmc.log('[ context.dg ]  menu item disabled: {0}'.format(id), LOGNOTICE)


class AddonCheckUpdate:
	def run(self):
		xbmc.log('[ context.dg ]  Addon checking available updates', LOGNOTICE)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/deangrice07/dg.github.io/blob/master/Matrix/Repository/zips/context.dg/addon.xml')
			if not repo_xml.status_code == 200:
				xbmc.log('[ context.dg ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, LOGNOTICE)
				return
			repo_version = re.findall(r'<addon id=\"context.dg\".+version=\"(\d*.\d*.\d*)\"', repo_xml.text)[0]
			local_version = xbmcaddon.Addon('context.dg').getAddonInfo('version')[:5] # 5 char max so pre-releases do try to compare more chars than github version
			def check_version_numbers(self, current, new): # Compares version numbers and return True if github version is newer
				current = current.split('.')
				new = new.split('.')
				step = 0
				for i in current:
					if int(new[step]) > int(i): return True
					if int(i) > int(new[step]): return False
					if int(i) == int(new[step]):
						step += 1
						continue
				return False
			if check_version_numbers(local_version, repo_version):
				while xbmc.getCondVisibility('Library.IsScanningVideo'):
					xbmc.sleep(10000)
				xbmc.log('[ context.dg ]  A newer version is available. Installed Version: v%s, Repo Version: v%s' % (local_version, repo_version), LOGNOTICE)
				message = 'A new verison of "DG - Global Context Menu Items" is available from the repository. Please consider updating to v%s'
				xbmcgui.Dialog().notification(title='context.dg', message=message % repo_version, icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)
		except:
			import traceback
			traceback.print_exc()

if xbmcaddon.Addon().getSetting('checkAddonUpdates') == 'true':
	AddonCheckUpdate().run()
	xbmc.log('[ context.dg ]  Addon update check complete', LOGNOTICE)

# start monitoring settings changes events
xbmc.log('[ context.dg ]  service started', LOGNOTICE)
properties_monitor = PropertiesUpdater()

# wait until abort is requested
properties_monitor.waitForAbort()
xbmc.log('[ context.dg ]  service stopped', LOGNOTICE)