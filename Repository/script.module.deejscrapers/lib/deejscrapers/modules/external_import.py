import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import os
import shutil
import json
from liptonscrapers import providerSources
from liptonscrapers.modules import control

dialog = xbmcgui.Dialog()

class ExternalImporter():
    def __init__(self):
        self.extPath = None
        self.useableAddons = [
        ('plugin.video.tempest', 'from resources.lib.', ['resources', 'lib', 'sources']),
        ('script.module.eggscrapers', 'from resources.lib.', ['lib', 'eggscrapers']),
        ('script.module.openscrapers', 'from openscrapers.', ['lib', 'openscrapers', 'sources_openscrapers']),
        ('script.module.exoscrapers', 'from exoscrapers.', ['lib', 'exoscrapers', 'sources_exoscrapers']),
	('script.module.tikiscrapers', 'from tikiscrapers.', ['lib', 'tikiscrapers', 'sources_tikiscrapers']),
        ('script.module.scrubsv2', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources']),
	('script.module.clownsreplica', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources']),
        ('script.module.yoda', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources']),
        ('script.module.numbersbynumbers', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources']),
        ('script.module.oathscrapers', 'from resources.lib.', ['lib', 'oathscrapers', 'sources_oathscrapers']),
 	('script.module.movietheaterbutter', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources']),
	('script.module.movietheaterbutter.auto', 'from resources.lib.', ['lib', 'resources', 'lib', 'sources'])
                        ]

    def importExternal(self):
        self.setImportAddon()
        if not self.extPath: return control.infoDialog('External Scrapers Activation Failed. Please See Log Error', time=5000)
        elif self.extPath == 'pass':
            return control.openSettings('0.7')
        else:
            control.busy()
            try:
                if xbmcvfs.exists(self.extPath):
                    try: xbmcvfs.rmdir(self.destPath, True)
                    except: pass
                    shutil.copytree(self.extPath, self.destPath)
                    self._removeGarbage(self.destPath)
                    self._instancesRename(self.destPath)
                    if not xbmcvfs.exists(self.backupPath):
                        shutil.copytree(self.destPath, self.backupPath)
                    control.infoDialog('[B]%s[/B] Activated' % self.extAddon.getAddonInfo('name'), icon=self.extAddon.getAddonInfo('icon'), time=5000)
                else:
                    control.infoDialog('Activation Failed. Please ensure you have Externals Scrapers Module Installed', 5000)
            except:
                control.infoDialog('External Scrapers Activation Failed. Please See Log Error', time=5000)
        control.idle()
        control.openSettings('0.7')
        return

    def removeExternal(self):
        try:
            sourceList = [i.lower() for i in sorted(providerSources()) if not i.lower() == 'liptonscrapers']
            enabledModules = [i for i in self.useableAddons if i[0].split('.')[-1] in sourceList]
            selectList = [xbmcgui.ListItem(self.addonInformation(i)[0].upper(), '[I]%s[/I]' % self.addonInformation(i)[1], iconImage=self.addonInformation(i)[2]) for i in enabledModules]
            if len(selectList) == 0:
                control.infoDialog('No External Scrapers to Remove', time=5000)
                return control.openSettings('0.8')
            select = dialog.select("Choose External Module", selectList, useDetails=True)
            control.idle()
            control.logger('select', select)
            if select == -1: return control.openSettings('0.8')
            moduleChoice = enabledModules[select][0]
            removeModule = 'sources_%s' % moduleChoice.split('.')[-1]
            removeFolder = xbmc.translatePath(os.path.join(control.addonInfo('path'), 'lib', 'liptonscrapers', removeModule + '/'))
            if xbmcvfs.exists(removeFolder):
                try: xbmcvfs.rmdir(removeFolder, True)
                except: pass
            self.removeBackup(removeModule)
            if control.setting('module.provider').lower() == moduleChoice.split('.')[-1]:
                control.setSetting('module.provider', 'Liptonscrapers')
            control.infoDialog('[B]%s[/B] Removed' % xbmcaddon.Addon(moduleChoice).getAddonInfo('name'), icon=xbmcaddon.Addon(moduleChoice).getAddonInfo('icon'), time=5000)
        except:
            control.infoDialog('External Scrapers Removal Failed. Please See Log Error', time=5000)
        control.openSettings('0.8')

    def importBackup(self, backupPath, module):
        destPath = xbmc.translatePath(os.path.join(control.addonInfo('path'), 'lib', 'liptonscrapers', module + '/'))
        if not xbmcvfs.exists(destPath):
            shutil.copytree(backupPath, destPath)

    def removeBackup(self, module):
        removePath = xbmc.translatePath(os.path.join(control.addonInfo('profile'), 'scraper_backups', module + '/'))
        if xbmcvfs.exists(removePath):
            xbmcvfs.rmdir(removePath, True)

    def setImportAddon(self):
        installedAddons = self.installedAddons()
        currentImports = [i.lower() for i in sorted(providerSources()) if not i.lower() == 'liptonscrapers']
        addons = [i for i in self.useableAddons if i[0] in installedAddons]
        addons = [i for i in addons if not i[0].split('.')[-1] in currentImports]
        addonList = [xbmcgui.ListItem(self.addonInformation(i)[0].upper(), '[I]%s[/I]' % self.addonInformation(i)[1], iconImage=self.addonInformation(i)[2]) for i in addons]
        if len(addonList) == 0:
            self.extPath = 'pass'
            control.infoDialog('No External Scrapers to Import', time=5000)
            return
        selected = dialog.select("Choose External Module", addonList, useDetails=True)
        if selected == -1:
            self.extPath = 'pass'
            return
        selected = addons[selected]
        self.moduleID = selected[0]
        self.replacement = selected[1]
        self.path = selected[2]
        self.extAddon = xbmcaddon.Addon(self.moduleID)
        self.sourcesFolder = self.moduleID.split('.')[-1]
        self.destPath = xbmc.translatePath(os.path.join(control.addonInfo('path'), 'lib', 'liptonscrapers', 'sources_%s' % self.sourcesFolder + '/'))
        self.backupPath = xbmc.translatePath(os.path.join(control.addonInfo('profile'), 'scraper_backups', 'sources_%s' % self.sourcesFolder + '/'))
        if len(self.path) == 2: self.extPath = xbmc.translatePath(os.path.join(self.extAddon.getAddonInfo('path'), self.path[0], self.path[1] + '/'))
        elif len(self.path) == 3: self.extPath = xbmc.translatePath(os.path.join(self.extAddon.getAddonInfo('path'), self.path[0], self.path[1], self.path[2] + '/'))
        elif len(self.path) == 4: self.extPath = xbmc.translatePath(os.path.join(self.extAddon.getAddonInfo('path'), self.path[0], self.path[1], self.path[2], self.path[3] + '/'))
        else: self.extPath = None

    def installedAddons(self):
        r = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddons", "id": "1"}')
        r = unicode(r, 'utf-8', errors='ignore')
        r = (json.loads(r))['result']['addons']
        addons = [(str(i['addonid'])) for i in r]
        return addons

    def addonInformation(self, item):
        name = xbmcaddon.Addon(id=item[0]).getAddonInfo('name')
        summary = xbmcaddon.Addon(id=item[0]).getAddonInfo('summary')
        icon = xbmcaddon.Addon(id=item[0]).getAddonInfo('icon')
        return (name, summary, icon)

    def _makeInitFile(self):
        initFile = xbmcvfs.File(os.path.join(xbmcaddon.Addon("plugin.video.furkit").getAddonInfo('profile'), '__init__.py'), 'w')
        initFile.close()

    def _listDirectory(self, path, absolute=False):
        directories, files = xbmcvfs.listdir(path)
        if absolute:
            for i in range(len(files)):
                files[i] = os.path.join(path, files[i])
            for i in range(len(directories)):
                directories[i] = os.path.join(path, directories[i])
        return directories, files

    def _removeGarbage(self, path):
        try:
            directories, files = self._listDirectory(path, absolute=True)
            for file in files:
                end_file = file.split('/')[-1]
                if end_file.startswith('.'):
                    xbmcvfs.delete(file)
            for directory in directories:
                end_directory = directory.split('/')[-1]
                if end_directory.startswith(('.', 'de', 'es', 'gr', 'pl', 'fr', 'ko', 'ru', 'en_direct')):
                    xbmcvfs.rmdir(directory + '/', True)
        except: pass

    def _instancesRename(self, path):
        replacements = [['%s' % self.replacement, 'from liptonscrapers.']]
        directories, files = self._listDirectory(path, absolute=True)
        for file in files:
            if file.endswith('.py'):
                self._replace(file, replacements)
        for directory in directories:
            self._instancesRename(directory)

    def _replace(self, path, valueFrom, valueTo=None):
        try:
            data = self._read(path)
            if not isinstance(valueFrom, list):
                valueFrom = [[valueFrom, valueTo]]
            for replacement in valueFrom:
                data = data.replace(replacement[0], replacement[1])
            self._write(path, data)
        except: pass

    def _read(self, path):
        try:
            file = xbmcvfs.File(path)
            result = file.read()
            file.close()
            return result.decode('utf-8')
        except: return None

    def _write(self, path, value):
        try:
            file = xbmcvfs.File(path, 'w')
            result = file.write(str(value.encode('utf-8')))
            file.close()
            return result
        except: pass
