# -*- coding: UTF-8 -*-

import pkgutil
import os

from . import sources_dgscrapers


try:
    import xbmcaddon
    __addon__ = xbmcaddon.Addon(id='script.module.dgscrapers')
except:
    __addon__ = None
    pass

def sources():
    try:
        sourceDict = []
        if __addon__ is not None:
            provider = __addon__.getSetting('package.folder')
        else:
            provider = 'dgscrapers'
        sourceFolder = getScraperFolder(provider)
        sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
        sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
        for i in sourceSubFolders:
            for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
                if is_pkg:
                    continue
                if enabledCheck(module_name):
                    try:
                        module = loader.find_module(module_name).load_module(module_name)
                        sourceDict.append((module_name, module.source()))
                    except:
                        pass
        return sourceDict
    except:
        return []


def enabledCheck(module_name):
    if __addon__ is not None:
        if __addon__.getSetting('provider.' + module_name) == 'true':
            return True
        else:
            return False
    return True


def providerSources():
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    return getModuleName(sourceSubFolders)


def providerNames():
    providerList = []
    provider = __addon__.getSetting('package.folder')
    sourceFolder = getScraperFolder(provider)
    sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
    sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
    for i in sourceSubFolders:
        for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
            if is_pkg:
                continue
            correctName = module_name.split('_')[0]
            providerList.append(correctName)
    return providerList


def getAllHosters():
    def _sources(sourceFolder, appendList):
        sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
        sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
        for i in sourceSubFolders:
            for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
                if is_pkg:
                    continue
                try: mn = str(module_name).split('_')[0]
                except: mn = str(module_name)
                appendList.append(mn)
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    appendList = []
    for item in sourceSubFolders:
        if item not in ['__pycache__', 'modules', 'cfscrape', 'pyaes']:
            _sources(item, appendList)
    return list(set(appendList))


def getScraperFolder(scraper_source):
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    return [i for i in sourceSubFolders if scraper_source.lower() in i.lower()][0]


def getModuleName(scraper_folders):
    nameList = []
    for s in scraper_folders:
        if not s in ['__pycache__', 'modules', 'cfscrape', 'pyaes']:
            try: nameList.append(s.split('_')[1].lower().title())
            except: pass
    return nameList
