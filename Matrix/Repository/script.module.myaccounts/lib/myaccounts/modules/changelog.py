# -*- coding: utf-8 -*-
"""
	My Accounts
"""

from myaccounts.modules.control import addonPath, addonVersion, joinPath
from myaccounts.windows.textviewer import TextViewerXML
from myaccounts.modules import py_tools

if py_tools.isPY2:
	from io import open #py2 open() does not support encoding param

def get():
	myaccounts_path = addonPath()
	myaccounts_version = addonVersion()
	changelogfile = joinPath(myaccounts_path, 'changelog.txt')
	r = open(changelogfile, 'r', encoding='utf-8', errors='ignore')
	text = r.read()
	r.close()
	heading = '[B]My Accounts -  v%s - ChangeLog[/B]' % myaccounts_version
	windows = TextViewerXML('textviewer.xml', myaccounts_path, heading=heading, text=text)
	windows.run()
	del windows