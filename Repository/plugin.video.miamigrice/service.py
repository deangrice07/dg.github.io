'''
#:::::::::::::::::::::#
#:'######':'########':#
#::: ## :::::: ## ::::#
#:.. ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#: ###### :::: ## ::::#
#:::::::::::::::::::::#

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
import threading
from resources.lib.modules import log_utils
from resources.lib.modules import control
from xbmc import (LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO,
                  LOGNONE, LOGNOTICE, LOGSEVERE, LOGWARNING)

addon_name = 'Miami Grice'
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
addon_path = xbmc.translatePath(('special://home/addons/plugin.video.miamigrice')).decode('utf-8')
module_path = xbmc.translatePath(('special://home/addons/script.module.miamigrice')).decode('utf-8')


def main():
    fum_ver = xbmcaddon.Addon(id='script.module.miamigrice').getAddonInfo('version')
    updated = xbmcaddon.Addon(id='plugin.video.miamigrice').getSetting('module_base')
    if updated == '' or updated is None:
        updated = '0'

    if str(fum_ver) == str(updated):
        return

    xbmcgui.Dialog().notification(addon_name, 'Setting up Free Providers', addon_icon)
    settings_xml_path = os.path.join(addon_path, 'resources/settings.xml')
    scraper_path = os.path.join(module_path, 'lib/resources/lib/sources/en')
    log('Miami Grice Scraper Path: %s' % (str(scraper_path)), LOGINFO)
    try:
        xml = openfile(settings_xml_path)
    except Exception:
        failure = traceback.format_exc()
        log('Miami Grice Service - Exception: \n %s' % (str(failure)), LOGINFO)
        return

    new_settings = []
    new_settings = '<category label="Free Providers">\n'
    for file in glob.glob("%s/*.py" % (scraper_path)):
        file = os.path.basename(file)
        if '__init__' not in file:
            file = file.replace('.py', '')
            new_settings += '        <setting id="provider.%s" type="bool" label="%s" default="true" />\n' % (
                file.lower(), file.upper())
    new_settings += '    </category>'

    xml = xml.replace('<category label="Free Providers"></category>', str(new_settings))
    savefile(settings_xml_path, xml)

    xbmcaddon.Addon(id='plugin.video.miamigrice').setSetting('module_base', fum_ver)
    xbmcgui.Dialog().notification(addon_name, 'Providers Updated', addon_icon)


    xbmcgui.Dialog().notification(addon_name, 'Setting up Debrid Providers', addon_icon)
    settings_xml_path = os.path.join(addon_path, 'resources/settings.xml')
    scraper_path = os.path.join(module_path, 'lib/resources/lib/sources/en_de')
    log('Miami Grice Scraper Path: %s' % (str(scraper_path)), LOGINFO)
    try:
        xml = openfile(settings_xml_path)
    except Exception:
        failure = traceback.format_exc()
        log('Miami Grice Service - Exception: \n %s' % (str(failure)), LOGINFO)
        return

    new_settings = []
    new_settings = '<category label="Debrid Only">\n'
    for file in glob.glob("%s/*.py" % (scraper_path)):
        file = os.path.basename(file)
        if '__init__' not in file:
            file = file.replace('.py', '')
            new_settings += '        <setting id="provider.%s" type="bool" label="%s" default="true" />\n' % (
                file.lower(), file.upper())
    new_settings += '    </category>'

    xml = xml.replace('<category label="Debrid Only"></category>', str(new_settings))
    savefile(settings_xml_path, xml)

    xbmcaddon.Addon(id='plugin.video.miamigrice').setSetting('module_base', fum_ver)
    xbmcgui.Dialog().notification(addon_name, 'Providers Updated', addon_icon)


    xbmcgui.Dialog().notification(addon_name, 'Setting up Torrent Providers', addon_icon)
    settings_xml_path = os.path.join(addon_path, 'resources/settings.xml')
    scraper_path = os.path.join(module_path, 'lib/resources/lib/sources/en_tor')
    log('Miami Grice Scraper Path: %s' % (str(scraper_path)), LOGINFO)
    try:
        xml = openfile(settings_xml_path)
    except Exception:
        failure = traceback.format_exc()
        log('Miami Grice Service - Exception: \n %s' % (str(failure)), LOGINFO)
        return

    new_settings = []
    new_settings = '<category label="Torrent (cached)">\n'
    for file in glob.glob("%s/*.py" % (scraper_path)):
        file = os.path.basename(file)
        if '__init__' not in file:
            file = file.replace('.py', '')
            new_settings += '        <setting id="provider.%s" type="bool" label="%s" default="true" />\n' % (
                file.lower(), file.upper())
    new_settings += '    </category>'

    xml = xml.replace('<category label="Torrent (cached)"></category>', str(new_settings))
    savefile(settings_xml_path, xml)

    xbmcaddon.Addon(id='plugin.video.miamigrice').setSetting('module_base', fum_ver)
    xbmcgui.Dialog().notification(addon_name, 'Providers Updated', addon_icon)
    
    
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


DEBUGPREFIX = '[COLOR red][ Miami Grice DEBUG ][/COLOR]'


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

def syncTraktLibrary():
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.miamigrice/?action=tvshowsToLibrarySilent&url=traktcollection')
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.miamigrice/?action=moviesToLibrarySilent&url=traktcollection')

if control.setting('autoTraktOnStart') == 'true':
    syncTraktLibrary()

if int(control.setting('schedTraktTime')) > 0:
    log_utils.log('###############################################################', log_utils.LOGNOTICE)
    log_utils.log('#################### STARTING TRAKT SCHEDULING ################', log_utils.LOGNOTICE)
    log_utils.log('#################### SCHEDULED TIME FRAME '+ control.setting('schedTraktTime')  + ' HOURS ################', log_utils.LOGNOTICE)
    timeout = 3600 * int(control.setting('schedTraktTime'))
    schedTrakt = threading.Timer(timeout, syncTraktLibrary)
    schedTrakt.start()