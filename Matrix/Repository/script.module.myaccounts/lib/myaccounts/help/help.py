# -*- coding: utf-8 -*-
"""
	My Accounts
"""

from myaccounts.modules import control

myaccounts_path = control.addonPath()
myaccounts_version = control.addonVersion()


def get(file):
	helpFile = control.joinPath(myaccounts_path, 'lib', 'myaccounts', 'help', file + '.txt')
	r = open(helpFile)
	text = r.read()
	r.close()
	control.dialog.textviewer('[COLOR red]My Accounts[/COLOR] -  v%s - %s' % (myaccounts_version, file), text)