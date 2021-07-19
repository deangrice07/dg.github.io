# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getdgVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get():
	dg_path = addonPath(addonId())
	dg_version = getdgVersion()
	changelogfile = joinPath(dg_path, 'changelog.txt')
	r = open(changelogfile)
	text = r.read()
	r.close()
	heading = '[B]DG -  v%s - ChangeLog[/B]' % dg_version
	windows = TextViewerXML('textviewer.xml', dg_path, heading=heading, text=text)
	windows.run()
	del windows
