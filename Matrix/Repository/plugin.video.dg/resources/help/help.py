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
	r = open(helpFile)
	text = r.read()
	r.close()
	heading = '[B]Venom -  v%s - %s[/B]' % (venom_version, file)
	windows = TextViewerXML('textviewer.xml', venom_path, heading=heading, text=text)
	windows.run()
	del windows