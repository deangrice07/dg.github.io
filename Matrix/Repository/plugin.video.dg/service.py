# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from resources.lib.modules import control, log_utils, my_accounts

window = control.homeWindow
plugin = 'plugin://plugin.video.dg/'
LOGINFO = 1

class CheckSettingsFile:
	def run(self):
		try:
			control.log('[ plugin.video.dg ]  CheckSettingsFile Service Starting...', LOGINFO)
			window.clearProperty('dg_settings')
			profile_dir = control.dataPath
			if not control.existsPath(profile_dir):
				success = control.makeDirs(profile_dir)
				if success: control.log('%s : created successfully' % profile_dir, LOGINFO)
			else: control.log('%s : already exists' % profile_dir, LOGINFO)
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			if not control.existsPath(settings_xml):
				control.setSetting('trakt.message2', '')
				control.log('%s : created successfully' % settings_xml, LOGINFO)
			else: control.log('%s : already exists' % settings_xml, LOGINFO)
			return control.log('[ plugin.video.dg ]  Finished CheckSettingsFile Service', LOGINFO)
		except:
			log_utils.error()

class SettingsMonitor(control.monitor_class):
	def __init__ (self):
		control.monitor_class.__init__(self)
		control.refresh_playAction()
		control.refresh_libPath()
		window.setProperty('dg.debug.reversed', control.setting('debug.reversed'))
		control.log('[ plugin.video.dg ]  Settings Monitor Service Starting...', LOGINFO)

	def onSettingsChanged(self): # Kodi callback when the addon settings are changed
		window.clearProperty('dg_settings')
		control.sleep(50)
		refreshed = control.make_settings_dict()
		control.refresh_playAction()
		control.refresh_libPath()
		control.refresh_debugReversed()

class SyncMyAccounts:
	def run(self):
		control.log('[ plugin.video.dg ]  Sync "My Accounts" Service Starting...', LOGINFO)
		my_accounts.syncMyAccounts(silent=True)
		return control.log('[ plugin.video.dg ]  Finished Sync "My Accounts" Service', LOGINFO)

class ReuseLanguageInvokerCheck:
	def run(self):
		control.log('[ plugin.video.dg ]  ReuseLanguageInvokerCheck Service Starting...', LOGINFO)
		try:
			import xml.etree.ElementTree as ET
			from resources.lib.modules.language_invoker import gen_file_hash
			addon_xml = control.joinPath(control.addonPath('plugin.video.dg'), 'addon.xml')
			tree = ET.parse(addon_xml)
			root = tree.getroot()
			current_addon_setting = control.addon('plugin.video.dg').getSetting('reuse.languageinvoker')
			try: current_xml_setting = [str(i.text) for i in root.iter('reuselanguageinvoker')][0]
			except: return control.log('[ plugin.video.dg ]  ReuseLanguageInvokerCheck failed to get settings.xml value', LOGINFO)
			if current_addon_setting == '':
				current_addon_setting = 'true'
				control.setSetting('reuse.languageinvoker', current_addon_setting)
			if current_xml_setting == current_addon_setting:
				return control.log('[ plugin.video.dg ]  ReuseLanguageInvokerCheck Service Finished', LOGINFO)
			control.okDialog(message='%s\n%s' % (control.lang(33023), control.lang(33020)))
			for item in root.iter('reuselanguageinvoker'):
				item.text = current_addon_setting
				hash_start = gen_file_hash(addon_xml)
				tree.write(addon_xml)
				hash_end = gen_file_hash(addon_xml)
				control.log('[ plugin.video.dg ]  ReuseLanguageInvokerCheck Service Finished', LOGINFO)
				if hash_start != hash_end:
					current_profile = control.infoLabel('system.profilename')
					control.execute('LoadProfile(%s)' % current_profile)
				else: control.okDialog(title='default', message=33022)
			return
		except:
			log_utils.error()

class AddonCheckUpdate:
	def run(self):
		control.log('[ plugin.video.dg ]  Addon checking available updates', LOGINFO)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/deangrice07/dg.github.io/master/Matrix/Repository/zips/addons.xml')
			if not repo_xml.status_code == 200:
				return control.log('[ plugin.video.dg ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, LOGINFO)
			repo_version = re.findall(r'<addon id=\"plugin.video.dg\".+version=\"(\d*.\d*.\d*)\"', repo_xml.text)[0]
			local_version = control.getdgVersion()[:5] # 5 char max so pre-releases do try to compare more chars than github version
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
				control.log('[ plugin.video.dg ]  A newer version is available. Installed Version: v%s, Repo Version: v%s' % (local_version, repo_version), LOGINFO)
				control.notification(message=control.lang(35523) % repo_version)
			return control.log('[ plugin.video.dg ]  Addon update check complete', LOGINFO)
		except:
			log_utils.error()

class VersionIsUpdateCheck:
	def run(self):
		try:
			from resources.lib.database import cache
			isUpdate = False
			oldVersion, isUpdate = cache.update_cache_version()
			if isUpdate:
				window.setProperty('dg.updated', 'true')
				curVersion = control.getdgVersion()
				clearDB_version = '6.3.1' # set to desired version to force any db clearing needed
				do_cacheClear = (int(oldVersion.replace('.', '')) < int(clearDB_version.replace('.', '')) <= int(curVersion.replace('.', '')))
				if do_cacheClear:
					clr_fanarttv = False
					cache.clrCache_version_update(clr_providers=False, clr_metacache=False, clr_cache=True, clr_search=False, clr_bookmarks=False)
					from resources.lib.database import traktsync
					clr_traktSync = {'bookmarks': True, 'hiddenProgress': False, 'liked_lists': False, 'movies_collection': False, 'movies_watchlist': False, 'public_lists': True,
											'popular_lists': True, 'service': False, 'shows_collection': False, 'shows_watchlist': False, 'trending_lists': True, 'user_lists': False}
					cleared = traktsync.delete_tables(clr_traktSync)
					if cleared:
						control.notification(message='Forced traktsync clear for version update complete.')
						control.log('[ plugin.video.dg ]  Forced traktsync clear for version update complete.', LOGINFO)
					if clr_fanarttv:
						from resources.lib.database import fanarttv_cache
						cleared = fanarttv_cache.cache_clear()
						control.notification(message='Forced fanarttv.db clear for version update complete.')
						control.log('[ plugin.video.dg ]  Forced fanarttv.db clear for version update complete.', LOGINFO)
				control.setSetting('trakt.message2', '') # force a settings write for any added settings may have been added in new version
				control.log('[ plugin.video.dg ]  Forced new User Data settings.xml saved', LOGINFO)
				control.log('[ plugin.video.dg ]  Plugin updated to v%s' % curVersion, LOGINFO)
		except:
			log_utils.error()

class SyncTraktCollection:
	def run(self):
		control.log('[ plugin.video.dg ]  Trakt Collection Sync Starting...', LOGINFO)
		control.execute('RunPlugin(%s?action=library_tvshowsToLibrarySilent&url=traktcollection)' % plugin)
		control.execute('RunPlugin(%s?action=library_moviesToLibrarySilent&url=traktcollection)' % plugin)
		control.log('[ plugin.video.dg ]  Trakt Collection Sync Complete', LOGINFO)

class LibraryService:
	def run(self):
		control.log('[ plugin.video.dg ]  Library Update Service Starting (Update check every 6hrs)...', LOGINFO)
		control.execute('RunPlugin(%s?action=service_library)' % plugin) # service_library contains control.monitor().waitForAbort() while loop every 6hrs

class SyncTraktService:
	def run(self):
		control.log('[ plugin.video.dg ]  Trakt Sync Service Starting (sync check every 15min)...', LOGINFO)
		control.execute('RunPlugin(%s?action=service_syncTrakt)' % plugin) # trakt.trakt_service_sync() contains control.monitor().waitForAbort() while loop every 15min

try:
	kodiVersion = control.getKodiVersion(full=True)
	addonVersion = control.addon('plugin.video.dg').getAddonInfo('version')
	repoVersion = control.addon('repository.dg').getAddonInfo('version')
	fsVersion = control.addon('script.module.fenomscrapers').getAddonInfo('version')
	maVersion = control.addon('script.module.myaccounts').getAddonInfo('version')
	log_utils.log('########   CURRENT dg VERSIONS REPORT   ########', level=log_utils.LOGINFO)
	log_utils.log('##   Kodi Version: %s' % str(kodiVersion), level=log_utils.LOGINFO)
	log_utils.log('##   python Version: %s' % str(control.pythonVersion), level=log_utils.LOGINFO)
	log_utils.log('##   plugin.video.dg Version: %s' % str(addonVersion), level=log_utils.LOGINFO)
	log_utils.log('##   repository.dg Version: %s' % str(repoVersion), level=log_utils.LOGINFO)
	log_utils.log('##   script.module.fenomscrapers Version: %s' % str(fsVersion), level=log_utils.LOGINFO)
	log_utils.log('##   script.module.myaccounts Version: %s' % str(maVersion), level=log_utils.LOGINFO)
	log_utils.log('######   DG SERVICE ENTERERING KEEP ALIVE   #####', level=log_utils.LOGINFO)
except:
	log_utils.log('## ERROR GETTING DG VERSION - Missing Repo or failed Install ', level=log_utils.LOGINFO)

def getTraktCredentialsInfo():
	username = control.setting('trakt.username').strip()
	token = control.setting('trakt.token')
	refresh = control.setting('trakt.refresh')
	if (username == '' or token == '' or refresh == ''): return False
	return True

def main():
	while not control.monitor.abortRequested():
		control.log('[ plugin.video.dg ]  Service Started', LOGINFO)
		schedTrakt = None
		libraryService = None
		CheckSettingsFile().run()
		SyncMyAccounts().run()
		ReuseLanguageInvokerCheck().run()
		if control.setting('library.service.update') == 'true':
			libraryService = True
			LibraryService().run()
		if control.setting('general.checkAddonUpdates') == 'true':
			AddonCheckUpdate().run()
		VersionIsUpdateCheck().run()
		SyncTraktService().run() # run service in case user auth's trakt later
		if getTraktCredentialsInfo():
			if control.setting('autoTraktOnStart') == 'true':
				SyncTraktCollection().run()
			if int(control.setting('schedTraktTime')) > 0:
				import threading
				log_utils.log('#################### STARTING TRAKT SCHEDULING ################', level=log_utils.LOGINFO)
				log_utils.log('#################### SCHEDULED TIME FRAME '+ control.setting('schedTraktTime')  + ' HOURS ###############', level=log_utils.LOGINFO)
				timeout = 3600 * int(control.setting('schedTraktTime'))
				schedTrakt = threading.Timer(timeout, SyncTraktCollection().run) # this only runs once at the designated interval time to wait...not repeating
				schedTrakt.start()
		break
	SettingsMonitor().waitForAbort()
	control.log('[ plugin.video.dg ]  Settings Monitor Service Stopping...', LOGINFO)
	control.log('[ plugin.video.dg ]  Trakt Sync Service Stopping...', LOGINFO)

	if libraryService:
		control.log('[ plugin.video.dg ]  Library Update Service Stopping...', LOGINFO)
	if schedTrakt:
		schedTrakt.cancel()
	control.log('[ plugin.video.dg ]  Service Stopped', LOGINFO)

main()