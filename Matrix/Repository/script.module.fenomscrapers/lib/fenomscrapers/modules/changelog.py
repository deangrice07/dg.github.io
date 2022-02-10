# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

from fenomscrapers.modules.control import addonPath, addonVersion, joinPath
from fenomscrapers.windows.textviewer import TextViewerXML
from fenomscrapers.modules import py_tools

if py_tools.isPY2:
	from io import open #py2 open() does not support encoding param

def get():
	fenomscrapers_path = addonPath()
	fenomscrapers_version = addonVersion()
	changelogfile = joinPath(fenomscrapers_path, 'changelog.txt')
	r = open(changelogfile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]FenomScrapers -  v%s - ChangeLog[/B]' % fenomscrapers_version
	windows = TextViewerXML('textviewer.xml', fenomscrapers_path, heading=heading, text=text)
	windows.run()
	del windows