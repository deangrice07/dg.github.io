# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

import xbmc
from fenomscrapers.modules import control
window = control.homeWindow
LOGNOTICE = xbmc.LOGNOTICE if control.getKodiVersion() < 19 else xbmc.LOGINFO # (2 in 18, deprecated in 19 use LOGINFO(1))


class CheckSettingsFile:
	def run(self):
		try:
			xbmc.log('[ script.module.fenomscrapers ]  CheckSettingsFile Service Starting...', LOGNOTICE)
			window.clearProperty('fenomscrapers_settings')
			profile_dir = control.dataPath
			if not control.existsPath(profile_dir):
				success = control.makeDirs(profile_dir)
				if success: xbmc.log('%s : created successfully' % profile_dir, LOGNOTICE)
			else: xbmc.log('%s : already exists' % profile_dir, LOGNOTICE)
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			if not control.existsPath(settings_xml):
				control.setSetting('module.provider', 'Fenomscrapers')
				xbmc.log('%s : created successfully' % settings_xml, LOGNOTICE)
			else: xbmc.log('%s : already exists' % settings_xml, LOGNOTICE)
			return xbmc.log('[ script.module.fenomscrapers ]  Finished CheckSettingsFile Service', LOGNOTICE)
		except:
			import traceback
			traceback.print_exc()


class SettingsMonitor(control.monitor_class):
	def __init__ (self):
		control.monitor_class.__init__(self)
		control.setUndesirables()
		xbmc.log('[ script.module.fenomscrapers ]  Settings Monitor Service Starting...', LOGNOTICE)

	def onSettingsChanged(self):
		# Kodi callback when the addon settings are changed
		window.clearProperty('fenomscrapers_settings')
		control.sleep(50)
		refreshed = control.make_settings_dict()
		control.setUndesirables()


class AddonCheckUpdate:
	def run(self):
		xbmc.log('[ script.module.fenomscrapers ]  Addon checking available updates', LOGNOTICE)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/mr-kodi/repository.fenomscrapers/master/zips/addons.xml')
			if not repo_xml.status_code == 200:
				return xbmc.log('[ script.module.fenomscrapers ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, LOGNOTICE)
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
				xbmc.log('[ script.module.fenomscrapers ]  A newer version is available. Installed Version: v%s, Repo Version: v%s' % (local_version, repo_version), LOGNOTICE)
				control.notification(message=control.lang(32037) % repo_version, time=5000)
			return xbmc.log('[ script.module.fenomscrapers ]  Addon update check complete', LOGNOTICE)
		except:
			import traceback
			traceback.print_exc()


class SyncMyAccounts:
	def run(self):
		xbmc.log('[ script.module.fenomscrapers ]  Sync "My Accounts" Service Starting...', LOGNOTICE)
		control.syncMyAccounts(silent=True)
		return xbmc.log('[ script.module.fenomscrapers ]  Finished Sync "My Accounts" Service', LOGNOTICE)


def main():
	while not control.monitor.abortRequested():
		xbmc.log('[ script.module.fenomscrapers ]  Service Started', LOGNOTICE)
		CheckSettingsFile().run()
		SyncMyAccounts().run()
		if control.setting('checkAddonUpdates') == 'true':
			AddonCheckUpdate().run()
		if control.isVersionUpdate():
			control.clean_settings()
			xbmc.log('[ script.module.fenomscrapers ]  Settings file cleaned complete', LOGNOTICE)
		SettingsMonitor().waitForAbort()
		xbmc.log('[ script.module.fenomscrapers ]  Service Stopped', LOGNOTICE)
		break

main()