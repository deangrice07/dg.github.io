# -*- coding: utf-8 -*-
"""
	Fenomscrapers Module
"""

from fenomscrapers.modules import control

fenomscrapers_path = control.addonPath()
fenomscrapers_version = control.addonVersion()


def get(file):
	helpFile = control.joinPath(fenomscrapers_path, 'lib', 'fenomscrapers', 'help', file + '.txt')
	r = open(helpFile)
	text = r.read()
	r.close()
	control.dialog.textviewer('[COLOR red]Fenomscrapers[/COLOR] -  v%s - %s' % (fenomscrapers_version, file), text)