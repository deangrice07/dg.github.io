# -*- coding: utf-8 -*-

'''

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import glob
import os
import re
import traceback

import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.modules import log_utils
from resources.lib.modules import control
from xbmc import (LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO,
                  LOGNONE, LOGNOTICE, LOGSEVERE, LOGWARNING)

addon_name = 'rooboys'
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
addon_path = xbmc.translatePath(('special://home/addons/plugin.video.rooboys')).decode('utf-8')
module_path = xbmc.translatePath(('special://home/addons/script.module.diamondscrapers')).decode('utf-8')

control.execute('RunPlugin(plugin://%s)' % control.get_plugin_url({'action': 'service'}))

def syncTraktLibrary():
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.rooboys/?action=tvshowsToLibrarySilent&url=traktcollection')
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.rooboys/?action=moviesToLibrarySilent&url=traktcollection')

try:
    ModuleVersion = control.addon('script.module.rooboys').getAddonInfo('version')
    AddonVersion = control.addon('plugin.video.rooboys').getAddonInfo('version')
    RepoVersion = control.addon('repository.griceadvicekodi').getAddonInfo('version')

    log_utils.log('######################### rooboys ############################', log_utils.LOGNOTICE)
    log_utils.log('####### CURRENT rooboys VERSIONS REPORT ######################', log_utils.LOGNOTICE)
    log_utils.log('### rooboys PLUGIN VERSION: %s ###' % str(AddonVersion), log_utils.LOGNOTICE)
    log_utils.log('### rooboys SCRIPT VERSION: %s ###' % str(ModuleVersion), log_utils.LOGNOTICE)
    log_utils.log('### rooboys REPOSITORY VERSION: %s ###' % str(RepoVersion), log_utils.LOGNOTICE)
    log_utils.log('###############################################################', log_utils.LOGNOTICE)
except:
    log_utils.log('######################### rooboys ############################', log_utils.LOGNOTICE)
    log_utils.log('####### CURRENT rooboys VERSIONS REPORT ######################', log_utils.LOGNOTICE)
    log_utils.log('### ERROR GETTING rooboys VERSIONS - NO HELP WILL BE GIVEN AS THIS IS NOT AN OFFICIAL rooboys INSTALL. ###', log_utils.LOGNOTICE)
    log_utils.log('###############################################################', log_utils.LOGNOTICE)

if control.setting('autoTraktOnStart') == 'true':
    syncTraktLibrary()

if int(control.setting('schedTraktTime')) > 0:
    log_utils.log('###############################################################', log_utils.LOGNOTICE)
    log_utils.log('#################### STARTING TRAKT SCHEDULING ################', log_utils.LOGNOTICE)
    log_utils.log('#################### SCHEDULED TIME FRAME '+ control.setting('schedTraktTime')  + ' HOURS ################', log_utils.LOGNOTICE)
    timeout = 3600 * int(control.setting('schedTraktTime'))
    schedTrakt = threading.Timer(timeout, syncTraktLibrary)
    schedTrakt.start()

def main():
    fum_ver = xbmcaddon.Addon(id='script.module.openscrapers').getAddonInfo('version')
    updated = xbmcaddon.Addon(id='plugin.video.rooboys').getSetting('module_base')
    if updated == '' or updated is None:
        updated = '0'

    if str(fum_ver) == str(updated):
        return

    xbmcgui.Dialog().notification(addon_name, 'Gathering scraper details', addon_icon)
    settings_xml_path = os.path.join(addon_path, 'resources/settings.xml')
    scraper_path = os.path.join(module_path, 'lib/resources/lib/sources/en')
    log('rooboys Scraper Path: %s' % (str(scraper_path)), LOGINFO)
    try:
        xml = openfile(settings_xml_path)
    except Exception:
        failure = traceback.format_exc()
        log('rooboys Service - Exception: \n %s' % (str(failure)), LOGINFO)
        return

    new_settings = []
    new_settings = '<category label="32345">\n'
    for file in glob.glob("%s/*.py" % (scraper_path)):
        file = os.path.basename(file)
        if '__init__' not in file:
            file = file.replace('.py', '')
            new_settings += '        <setting id="provider.%s" type="bool" label="%s" default="true" />\n' % (
                file.lower(), file.upper())
    new_settings += '    </category>'

    xml = xml.replace('<category label="32345"></category>', str(new_settings))
    savefile(settings_xml_path, xml)

    xbmcaddon.Addon(id='plugin.video.rooboys').setSetting('module_base', fum_ver)
    xbmcgui.Dialog().notification(addon_name, 'Scraper settings updated', addon_icon)


def openfile(path_to_the_file):
    try:
        fh = open(path_to_the_file, 'rb')
        contents = fh.read()
        fh.close()
        return contents
    except Exception:
        failure = traceback.format_exc()
        print('Service Open File Exception - %s \n %s' % (path_to_the_file, str(failure)))
        return None


def savefile(path_to_the_file, content):
    try:
        fh = open(path_to_the_file, 'wb')
        fh.write(content)
        fh.close()
    except Exception:
        failure = traceback.format_exc()
        print('Service Save File Exception - %s \n %s' % (path_to_the_file, str(failure)))


DEBUGPREFIX = '[ ROOBOYS [COLOR red]DEBUG[/COLOR] ]'


def log(msg, level=LOGNOTICE):

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))
        print('%s: %s' % (DEBUGPREFIX, msg))
    except Exception as e:
        try:
            xbmc.log('Logging Failure: %s' % (e), level)
        except Exception:
            pass

if __name__ == '__main__':
    main()
