# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

import xbmc
from fenomscrapers.modules import control
window = control.homeWindow
LOGINFO = 1 # (LOGNOTICE(2) deprecated in 19, use LOGINFO(1))

class CheckSettingsFile:
	def run(self):
		try:
			xbmc.log('[ script.module.fenomscrapers ]  CheckSettingsFile Service Starting...', LOGINFO)
			window.clearProperty('fenomscrapers_settings')
			profile_dir = control.dataPath
			if not control.existsPath(profile_dir):
				success = control.makeDirs(profile_dir)
				if success: xbmc.log('%s : created successfully' % profile_dir, LOGINFO)
			else: xbmc.log('%s : already exists' % profile_dir, LOGINFO)
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			if not control.existsPath(settings_xml):
				control.setSetting('module.provider', 'Fenomscrapers')
				xbmc.log('%s : created successfully' % settings_xml, LOGINFO)
			else: xbmc.log('%s : already exists' % settings_xml, LOGINFO)
			return xbmc.log('[ script.module.fenomscrapers ]  Finished CheckSettingsFile Service', LOGINFO)
		except:
			import traceback
			traceback.print_exc()

class SettingsMonitor(control.monitor_class):
	def __init__ (self):
		control.monitor_class.__init__(self)
		window.setProperty('fenomscrapers.debug.reversed', control.setting('debug.reversed'))
		xbmc.log('[ script.module.fenomscrapers ]  Settings Monitor Service Starting...', LOGINFO)

	def onSettingsChanged(self): # Kodi callback when the addon settings are changed
		window.clearProperty('fenomscrapers_settings')
		control.sleep(50)
		refreshed = control.make_settings_dict()
		control.refresh_debugReversed()

class AddonCheckUpdate:
	def run(self):
		xbmc.log('[ script.module.fenomscrapers ]  Addon checking available updates', LOGINFO)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/mr-kodi/repository.fenomscrapers/master/zips/addons.xml')
			if repo_xml.status_code != 200:
				return xbmc.log('[ script.module.fenomscrapers ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, LOGINFO)
			repo_version = re.search(r'<addon id=\"script.module.fenomscrapers\".*version=\"(\d*.\d*.\d*)\"', repo_xml.text, re.I).group(1)
			local_version = control.addonVersion()[:5] # 5 char max so pre-releases do try to compare more chars than github version
			def check_version_numbers(current, new): # Compares version numbers and return True if github version is newer
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
				while control.condVisibility('Library.IsScanningVideo'):
					control.sleep(10000)
				xbmc.log('[ script.module.fenomscrapers ]  A newer version is available. Installed Version: v%s, Repo Version: v%s' % (local_version, repo_version), LOGINFO)
				control.notification(message=control.lang(32037) % repo_version, time=5000)
			return xbmc.log('[ script.module.fenomscrapers ]  Addon update check complete', LOGINFO)
		except:
			import traceback
			traceback.print_exc()

class SyncMyAccounts:
	def run(self):
		xbmc.log('[ script.module.fenomscrapers ]  Sync "My Accounts" Service Starting...', LOGINFO)
		control.syncMyAccounts(silent=True)
		return xbmc.log('[ script.module.fenomscrapers ]  Finished Sync "My Accounts" Service', LOGINFO)

class CheckUndesirablesDatabase:
	def run(self):
		xbmc.log('[ script.module.fenomscrapers ]  "CheckUndesirablesDatabase" Service Starting...', LOGINFO)
		from fenomscrapers.modules import undesirables
		try:
			old_database = undesirables.Undesirables().check_database()
			if old_database: undesirables.add_new_default_keywords()
		except:
			import traceback
			traceback.print_exc()
		return xbmc.log('[ script.module.fenomscrapers ]  Finished "CheckUndesirablesDatabase" Service', LOGINFO)

def main():
	while not control.monitor.abortRequested():
		xbmc.log('[ script.module.fenomscrapers ]  Service Started', LOGINFO)
		CheckSettingsFile().run()
		CheckUndesirablesDatabase().run()
		SyncMyAccounts().run()
		if control.setting('checkAddonUpdates') == 'true':
			AddonCheckUpdate().run()
		if control.isVersionUpdate():
			control.clean_settings()
			xbmc.log('[ script.module.fenomscrapers ]  Settings file cleaned complete', LOGINFO)
		SettingsMonitor().waitForAbort()
		xbmc.log('[ script.module.fenomscrapers ]  Service Stopped', LOGINFO)
		break

main()