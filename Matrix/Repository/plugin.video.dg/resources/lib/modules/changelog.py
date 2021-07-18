# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getVenomVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get():
	venom_path = addonPath(addonId())
	venom_version = getVenomVersion()
	changelogfile = joinPath(venom_path, 'changelog.txt')
	r = open(changelogfile)
	text = r.read()
	r.close()
	heading = '[B]DG -  v%s - ChangeLog[/B]' % venom_version
	windows = TextViewerXML('textviewer.xml', venom_path, heading=heading, text=text)
	windows.run()
	del windows
