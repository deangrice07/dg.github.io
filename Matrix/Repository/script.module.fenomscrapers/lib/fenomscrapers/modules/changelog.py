# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

from fenomscrapers.modules import control

fenomscrapers_path = control.addonPath()
fenomscrapers_version = control.addonVersion()
changelogfile = control.joinPath(fenomscrapers_path, 'changelog.txt')


def get():
	r = open(changelogfile)
	text = r.read()
	r.close()
	control.dialog.textviewer('[COLOR red]Fenomscrapers[/COLOR] -  v%s - ChangeLog' % fenomscrapers_version, text)