# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getDgVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get(file):
	dg_path = addonPath(addonId())
	dg_version = getDgVersion()
	helpFile = joinPath(dg_path, 'resources', 'help', file + '.txt')
	f = open(helpFile, 'r', encoding='utf-8', errors='ignore')
	text = f.read()
	f.close()
	heading = '[B]DG -  v%s - %s[/B]' % (dg_version, file)
	windows = TextViewerXML('textviewer.xml', dg_path, heading=heading, text=text)
	windows.run()
	del windows