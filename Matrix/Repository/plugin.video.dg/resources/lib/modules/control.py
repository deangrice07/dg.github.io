# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from datetime import datetime
from json import dumps as jsdumps, loads as jsloads
import os.path
from string import printable
from sys import version_info
import time
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import xml.etree.ElementTree as ET

pythonVersion = '{}.{}.{}'.format(version_info[0], version_info[1], version_info[2])
addon = xbmcaddon.Addon
AddonID = xbmcaddon.Addon().getAddonInfo('id')
addonInfo = xbmcaddon.Addon().getAddonInfo
addonName = addonInfo('name')
addonVersion = addonInfo('version')
getLangString = xbmcaddon.Addon().getLocalizedString

dialog = xbmcgui.Dialog()
getCurrentDialogId = xbmcgui.getCurrentWindowDialogId()
getCurrentWindowId = xbmcgui.getCurrentWindowId()
homeWindow = xbmcgui.Window(10000)
item = xbmcgui.ListItem
progressDialog = xbmcgui.DialogProgress()
progressDialogBG = xbmcgui.DialogProgressBG()

addItem = xbmcplugin.addDirectoryItem
content = xbmcplugin.setContent
directory = xbmcplugin.endOfDirectory
property = xbmcplugin.setProperty
resolve = xbmcplugin.setResolvedUrl
sortMethod = xbmcplugin.addSortMethod

condVisibility = xbmc.getCondVisibility
execute = xbmc.executebuiltin
infoLabel = xbmc.getInfoLabel
jsonrpc = xbmc.executeJSONRPC
keyboard = xbmc.Keyboard
legalFilename = xbmcvfs.makeLegalFilename
log = xbmc.log
monitor_class = xbmc.Monitor
monitor = monitor_class()
player = xbmc.Player()
player2 = xbmc.Player
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
skin = xbmc.getSkinDir()
transPath = xbmcvfs.translatePath

deleteDir = xbmcvfs.rmdir
deleteFile = xbmcvfs.delete
existsPath = xbmcvfs.exists
listDir = xbmcvfs.listdir
makeFile = xbmcvfs.mkdir
makeDirs = xbmcvfs.mkdirs
openFile = xbmcvfs.File

joinPath = os.path.join
isfilePath = os.path.isfile
absPath = os.path.abspath

SETTINGS_PATH = transPath(joinPath(addonInfo('path'), 'resources', 'settings.xml'))
try: dataPath = transPath(addonInfo('profile')).decode('utf-8')
except: dataPath = transPath(addonInfo('profile'))
settingsFile = joinPath(dataPath, 'settings.xml')
viewsFile = joinPath(dataPath, 'views.db')
bookmarksFile = joinPath(dataPath, 'bookmarks.db')
providercacheFile = joinPath(dataPath, 'providers.db')
metacacheFile = joinPath(dataPath, 'metadata.db')
searchFile = joinPath(dataPath, 'search.db')
libcacheFile = joinPath(dataPath, 'library.db')
cacheFile = joinPath(dataPath, 'cache.db')
traktSyncFile = joinPath(dataPath, 'traktSync.db')
trailer = 'plugin://plugin.video.youtube/play/?video_id=%s'

def getKodiVersion(full=False):
	if full: return xbmc.getInfoLabel("System.BuildVersion")
	else: return int(xbmc.getInfoLabel("System.BuildVersion")[:2])

def setting(id, fallback=None):
	try: settings_dict = jsloads(homeWindow.getProperty('dg_settings'))
	except: settings_dict = make_settings_dict()
	if settings_dict is None: settings_dict = settings_fallback(id)
	value = settings_dict.get(id, '')
	if fallback is None: return value
	if value == '': return fallback
	return value

def settings_fallback(id):
	return {id: xbmcaddon.Addon().getSetting(id)}

def setSetting(id, value):
	xbmcaddon.Addon().setSetting(id, value)

def make_settings_dict(): # service runs upon a setting change
	try:
		root = ET.parse(settingsFile).getroot()
		settings_dict = {}
		for item in root:
			dict_item = {}
			setting_id = item.get('id')
			setting_value = item.text
			if setting_value is None: setting_value = ''
			dict_item = {setting_id: setting_value}
			settings_dict.update(dict_item)
		homeWindow.setProperty('dg_settings', jsdumps(settings_dict))
		refresh_playAction()
		refresh_libPath()
		return settings_dict
	except:
		return None

def openSettings(query=None, id=addonInfo('id')):
	try:
		hide()
		execute('Addon.OpenSettings(%s)' % id)
		if not query: return
		c, f = query.split('.')
		execute('SetFocus(%i)' % (int(c) - 100))
		execute('SetFocus(%i)' % (int(f) - 80))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def lang(language_id):
	text = getLangString(language_id)
	return str(text)

def sleep(time):  # Modified `sleep`(in milli secs) that honors a user exit request
	while time > 0 and not monitor.abortRequested():
		xbmc.sleep(min(100, time))
		time = time - 100

def getCurrentViewId():
	win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	return str(win.getFocusId())

def getdgVersion():
	return xbmcaddon.Addon('plugin.video.dg').getAddonInfo('version')

def addonVersion(addon):
	return xbmcaddon.Addon(addon).getAddonInfo('version')

def addonId():
	return addonInfo('id')

def addonName():
	return addonInfo('name')

def addonPath(addon):
	try: addonID = xbmcaddon.Addon(addon)
	except: addonID = None
	if addonID is None: return ''
	else:
		try: return transPath(addonID.getAddonInfo('path').decode('utf-8'))
		except: return transPath(addonID.getAddonInfo('path'))

def artPath():
	theme = appearance()
	return joinPath(xbmcaddon.Addon('plugin.video.dg').getAddonInfo('path'), 'resources', 'artwork', theme)

def appearance():
	appearance = setting('appearance.1').lower()
	return appearance

def addonIcon():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'icon.png')
	return addonInfo('icon')

def addonThumb():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'poster.png')
	elif theme == '-': return 'DefaultFolder.png'
	return addonInfo('icon')

def addonPoster():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'poster.png')
	return 'DefaultVideo.png'

def addonFanart():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'fanart.jpg')
	return addonInfo('fanart')

def addonBanner():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'banner.png')
	return 'DefaultVideo.png'

def addonNext():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ['-', '']): return joinPath(art, 'next.png')
	return 'DefaultVideo.png'

####################################################
# --- Dialogs
####################################################
def notification(title=None, message=None, icon=None, time=3000, sound=(setting('notification.sound') == 'true')):
	if title == 'default' or title is None: title = addonName()
	if isinstance(title, int): heading = lang(title)
	else: heading = str(title)
	if isinstance(message, int): body = lang(message)
	else: body = str(message)
	if not icon or icon == 'default': icon = addonIcon()
	elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
	elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
	elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
	return dialog.notification(heading, body, icon, time, sound)

def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel=''):
	message = '%s[CR]%s[CR]%s' % (line1, line2, line3)
	return dialog.yesno(heading, message, nolabel, yeslabel)

def yesnocustomDialog(line1, line2, line3, heading=addonInfo('name'), customlabel='', nolabel='', yeslabel=''):
	message = '%s[CR]%s[CR]%s' % (line1, line2, line3)
	return dialog.yesnocustom(heading, message, customlabel, nolabel, yeslabel)

def selectDialog(list, heading=addonInfo('name')):
	return dialog.select(heading, list)

def okDialog(title=None, message=None):
	if title == 'default' or title is None: title = addonName()
	if isinstance(title, int): heading = lang(title)
	else: heading = str(title)
	if isinstance(message, int): body = lang(message)
	else: body = str(message)
	return dialog.ok(heading, body)

def context(items=None, labels=None):
	if items:
		labels = [i[0] for i in items]
		choice = dialog.contextmenu(labels)
		if choice >= 0: return items[choice][1]()
		else: return False
	else: return dialog.contextmenu(labels)


####################################################
# --- Built-in
####################################################
def busy():
	return execute('ActivateWindow(busydialognocancel)')

def hide():
	execute('Dialog.Close(busydialog)')
	execute('Dialog.Close(busydialognocancel)')

def closeAll():
	return execute('Dialog.Close(all,true)')

def closeOk():
	return execute('Dialog.Close(okdialog,true)')

def refresh():
	return execute('Container.Refresh')

def queueItem():
	return execute('Action(Queue)')

def refreshRepos():
	return execute('UpdateAddonRepos')
########################

def cancelPlayback():
	try:
		from sys import argv
		playlist.clear()
		resolve(int(argv[1]), False, item(offscreen=True))
		closeOk()
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def apiLanguage(ret_name=None):
	langDict = {'Bulgarian': 'bg', 'Chinese': 'zh', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Finnish': 'fi',
					'French': 'fr', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he', 'Hungarian': 'hu', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko',
					'Norwegian': 'no', 'Polish': 'pl', 'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk',
						'Slovenian': 'sl', 'Spanish': 'es', 'Swedish': 'sv', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk'}
	trakt = ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'th', 'tr', 'uk', 'zh']
	tvdb = ['en', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'fr', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'zh', 'cs', 'sl', 'hr', 'ko']
	youtube = ['gv', 'gu', 'gd', 'ga', 'gn', 'gl', 'ty', 'tw', 'tt', 'tr', 'ts', 'tn', 'to', 'tl', 'tk', 'th', 'ti', 'tg', 'te', 'ta', 'de', 'da', 'dz', 'dv', 'qu', 'zh', 'za', 'zu',
					'wa', 'wo', 'jv', 'ja', 'ch', 'co', 'ca', 'ce', 'cy', 'cs', 'cr', 'cv', 'cu', 'ps', 'pt', 'pa', 'pi', 'pl', 'mg', 'ml', 'mn', 'mi', 'mh', 'mk', 'mt', 'ms',
					'mr', 'my', 've', 'vi', 'is', 'iu', 'it', 'vo', 'ii', 'ik', 'io', 'ia', 'ie', 'id', 'ig', 'fr', 'fy', 'fa', 'ff', 'fi', 'fj', 'fo', 'ss', 'sr', 'sq', 'sw', 'sv', 'su', 'st', 'sk',
					'si', 'so', 'sn', 'sm', 'sl', 'sc', 'sa', 'sg', 'se', 'sd', 'lg', 'lb', 'la', 'ln', 'lo', 'li', 'lv', 'lt', 'lu', 'yi', 'yo', 'el', 'eo', 'en', 'ee', 'eu', 'et', 'es', 'ru',
					'rw', 'rm', 'rn', 'ro', 'be', 'bg', 'ba', 'bm', 'bn', 'bo', 'bh', 'bi', 'br', 'bs', 'om', 'oj', 'oc', 'os', 'or', 'xh', 'hz', 'hy', 'hr', 'ht', 'hu', 'hi', 'ho',
					'ha', 'he', 'uz', 'ur', 'uk', 'ug', 'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'as', 'ar', 'av', 'ay', 'az', 'nl', 'nn', 'no', 'na', 'nb', 'nd', 'ne', 'ng',
					'ny', 'nr', 'nv', 'ka', 'kg', 'kk', 'kj', 'ki', 'ko', 'kn', 'km', 'kl', 'ks', 'kr', 'kw', 'kv', 'ku', 'ky']
	tmdb = ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'th', 'tr', 'uk', 'zh']
	name = None
	name = setting('api.language')
	if not name: name = 'AUTO'
	if name[-1].isupper():
		try: name = xbmc.getLanguage(xbmc.ENGLISH_NAME).split(' ')[0]
		except: pass
	try: name = langDict[name]
	except: name = 'en'
	lang = {'trakt': name} if name in trakt else {'trakt': 'en'}
	lang['tvdb'] = name if name in tvdb else 'en'
	lang['youtube'] = name if name in youtube else 'en'
	lang['tmdb'] = name if name in tmdb else 'en'
	if ret_name:
		lang['trakt'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['trakt']][0]
		lang['tvdb'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['tvdb']][0]
		lang['youtube'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['youtube']][0]
		lang['tmdb'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['tmdb']][0]
	return lang

def autoTraktSubscription(tvshowtitle, year, imdb, tvdb): #---start adding TMDb to params
	from resources.lib.modules import library
	library.libtvshows().add(tvshowtitle, year, imdb, tvdb)

def getColor(n):
	colorChart = ['blue', 'red', 'yellow', 'deeppink', 'cyan', 'lawngreen', 'gold', 'magenta', 'yellowgreen',
						'skyblue', 'lime', 'limegreen', 'deepskyblue', 'white', 'whitesmoke', 'nocolor']
	if not n: n = '8'
	color = colorChart[int(n)]
	return color

def getSourceHighlightColor():
	n = setting('sources.highlight.color')
	colorChart = ['blue', 'red', 'yellow', 'deeppink', 'cyan', 'lawngreen', 'gold', 'magenta', 'yellowgreen',
						'skyblue', 'lime', 'limegreen', 'deepskyblue', 'white', 'whitesmoke', 'nocolor']
	if not n: n = '8'
	color = colorChart[int(n)]
	return color

def getMenuEnabled(menu_title):
	is_enabled = setting(menu_title).strip()
	if (is_enabled == '' or is_enabled == 'false'): return False
	return True

def trigger_widget_refresh(): # should prob make this run only on "isdg_widget"
	import time
	timestr = time.strftime("%Y%m%d%H%M%S", time.gmtime())
	homeWindow.setProperty("widgetreload", timestr)
	# homeWindow.setProperty('widgetreload-tvshows', timestr) # does not appear used
	homeWindow.setProperty('widgetreload-episodes', timestr)
	homeWindow.setProperty('widgetreload-movies', timestr)
	# execute('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)') # make sure this is ok coupled with above

def refresh_playAction(): # for dg global CM play actions
	play_mode = setting('play.mode')
	autoPlay = 'true' if play_mode == '1' else ''
	homeWindow.setProperty('dg.autoPlay.enabled', autoPlay)

def refresh_libPath(): # for dg global CM library actions
	homeWindow.setProperty('dg.movieLib.path', transPath(setting('library.movie')))
	homeWindow.setProperty('dg.tvLib.path', transPath(setting('library.tv')))

def datetime_workaround(string_date, format="%Y-%m-%d", date_only=True):
	sleep(200)
	try:
		if string_date == '': return None
		try:
			if date_only: res = datetime.strptime(string_date, format).date()
			else: res = datetime.strptime(string_date, format)
		except TypeError:
			if date_only: res = datetime(*(time.strptime(string_date, format)[0:6])).date()
			else: res = datetime(*(time.strptime(string_date, format)[0:6]))
		return res
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def metadataClean(metadata):
	if not metadata: return metadata
	allowed = ['genre', 'country', 'year', 'episode', 'season', 'sortepisode', 'sortseason', 'episodeguide', 'showlink',
					'top250', 'setid', 'tracknumber', 'rating', 'userrating', 'watched', 'playcount', 'overlay', 'cast', 'castandrole',
					'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer',
					'tvshowtitle', 'premiered', 'status', 'set', 'setoverview', 'tag', 'imdbnumber', 'code', 'aired', 'credits', 'lastplayed',
					'album', 'artist', 'votes', 'path', 'trailer', 'dateadded', 'mediatype', 'dbid']
	return {k: v for k, v in iter(metadata.items()) if k in allowed}

def strip_non_ascii_and_unprintable(text):
	try:
		result = ''.join(char for char in text if char in printable)
		return result.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return text
