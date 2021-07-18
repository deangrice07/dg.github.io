# -*- coding: utf-8 -*-
"""
	My Accounts
"""

from myaccounts.modules import control

myaccounts_path = control.addonPath()
myaccounts_version = control.addonVersion()
changelogfile = control.joinPath(myaccounts_path, 'changelog.txt')


def get():
	r = open(changelogfile)
	text = r.read()
	r.close()
	control.dialog.textviewer('[COLOR red]My Accounts[/COLOR] -  v%s - ChangeLog' % myaccounts_version, text)