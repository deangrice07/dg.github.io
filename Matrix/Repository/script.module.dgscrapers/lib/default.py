# -*- coding: utf-8 -*-

import sys, base64
import six
from six.moves import urllib_parse
from dgscrapers import sources_dgscrapers
from dgscrapers.modules import control
from dgscrapers import providerSources, providerNames


params = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?', '')))
action = params.get('action')
mode = params.get('mode')
query = params.get('query')


fix = '3Vk5GbtJmN4kHT65UbjBnQIRmZxIjYrZFSixWOxIGaShUY65UbjhmQYpVeONDT'.encode('utf-8')
d = base64.b64decode(base64.b64decode(fix[::-1] + b'h3')).replace(b'_', b'.')[::-1]
d = six.ensure_text(d)
if not sys.argv[0] == d:
    sys.exit()

def ScraperChoice():
    from dgscrapers import providerSources
    sourceList = providerSources()
    control.idle()
    select = control.selectDialog([i for i in sourceList])
    if select == -1: return
    module_choice = sourceList[select]
    control.setSetting('package.folder', module_choice)
    control.sleep(200)
    control.openSettings('0.1')

def ToggleProviderAll(enable):
    from dgscrapers import providerNames
    sourceList = providerNames()
    (setting, open_id) = ('true', '0.3') if enable else ('false', '0.2')
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, setting)
    control.sleep(200)
    control.openSettings(open_id)


if action == "dgscrapersettings":
    control.openSettings('0.0', 'script.module.dgscrapers')

elif mode == "dgscrapersettings":
    control.openSettings('0.0', 'script.module.dgscrapers')


elif action == "ScraperChoice":
    ScraperChoice()


elif mode == "ScraperChoice":
    ScraperChoice()


elif action == "toggleAll":
    sourceList = []
    sourceList = sources_dgscrapers.all_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All providers = %s' % sourceList,2)
    control.sleep(200)
    control.openSettings(query, "script.module.dgscrapers")


elif action == "ToggleProviderAll":
    ToggleProviderAll(False if params['action'] == "DisableModuleAll" else True)


elif action == "toggleAllHosters":
    sourceList = []
    sourceList = sources_dgscrapers.hoster_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Hoster providers = %s' % sourceList,2)
    control.sleep(200)
    control.openSettings(query, "script.module.dgscrapers")


elif action == "toggleAllForeign":
    sourceList = []
    sourceList = sources_dgscrapers.all_foreign_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Foregin providers = %s' % sourceList,2)
    control.sleep(200)
    control.openSettings(query, "script.module.dgscrapers")


elif action == "toggleAllGreek":
    sourceList = []
    sourceList = sources_dgscrapers.greek_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Greek providers = %s' % sourceList,2)
    control.sleep(200)
    control.openSettings(query, "script.module.dgscrapers")


elif action == "toggleAllTorrent":
    sourceList = []
    sourceList = sources_dgscrapers.torrent_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Torrent providers = %s' % sourceList,2)
    control.sleep(200)
    control.openSettings(query, "script.module.dgscrapers")


elif action == "Defaults":
     sourceList = ['123fox','123hbo','123movieshubz','animetoon','azmovies','bnwmovies','cartoonhd',
	 'extramovies','fmovies','freefmovies','freeputlockers','gostream','Hdmto','hdpopcorns',
     'kattv','l23movies','iwaatch','openloadmovie','primewire','putlocker','reddit','rlsbb','scenerls',
     'seehd','series9','seriesfree','seriesonline','solarmoviez','tvbox','vidics','watchseries',
     'xwatchseries','vdonip','downflix','ymovies','ddlspot','filmxy','kickass2','sezonlukdizi']
	 for i in sourceList:
         source_setting = 'provider.' + i
         control.setSetting(source_setting, params['setting'])
     control.sleep(200)
     control.openSettings(query, "script.module.dgscrapers")

