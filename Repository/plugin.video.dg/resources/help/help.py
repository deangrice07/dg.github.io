# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getVenomVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get(file):
	venom_path = addonPath(addonId())
	venom_version = getVenomVersion()
	helpFile = joinPath(venom_path, 'resources', 'help', file + '.txt')
	f = open(helpFile, 'r', encoding='utf-8', errors='ignore')
	text = f.read()
	f.close()
	heading = '[B]Venom -  v%s - %s[/B]' % (venom_version, file)
	windows = TextViewerXML('textviewer.xml', venom_path, heading=heading, text=text)
	windows.run()
	del windows