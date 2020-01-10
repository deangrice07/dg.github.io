# -*- coding: utf-8 -*-

import threading
from resources.lib.modules import control,log_utils

control.execute('RunPlugin(plugin://%s)' % control.get_plugin_url({'action': 'service'}))

try:
    AddonVersion = control.addon('plugin.video.deej').getAddonInfo('version')
    ModuleVersion = control.addon('plugin.video.deej').getAddonInfo('version')
    RepoVersion = control.addon('repository.griceadvicekodi').getAddonInfo('version')
    log_utils.log('===-[AddonVersion: %s]-' % str(AddonVersion) + '-[ModuleVersion: %s]-' % str(ModuleVersion) + '-[RepoVersion: %s]-' % str(RepoVersion), log_utils.LOGNOTICE)
except:
    log_utils.log('===-[Error', log_utils.LOGNOTICE)
    log_utils.log('===-[Had Trouble Getting Version Info. Make Sure You Have the Grice Advice Repo.', log_utils.LOGNOTICE)

def syncTraktLibrary():
    control.execute('RunPlugin(plugin://%s)' % 'plugin.video.deej/?action=tvshowsToLibrarySilent&url=traktcollection')
    control.execute('RunPlugin(plugin://%s)' % 'plugin.video.deej/?action=moviesToLibrarySilent&url=traktcollection')

if control.setting('autoTraktOnStart') == 'true':
    syncTraktLibrary()

"""if int(control.setting('schedTraktTime')) > 0:
    log_utils.log('===-[Starting Trakt Scheduling.', log_utils.LOGNOTICE)
    log_utils.log('===-[Scheduled Time Frame '+ control.setting('schedTraktTime')  + ' Hours.', log_utils.LOGNOTICE)
    timeout = 3600 * int(control.setting('schedTraktTime'))
    schedTrakt = threading.Timer(timeout, syncTraktLibrary)
    schedTrakt.start()
"""
