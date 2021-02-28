# -*- coding: utf-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# @tantrumdev wrote this file.  As long as you retain this notice you can do whatever you want with this
# stuff. Just please ask before copying. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################

# Addon Name: New
# Addon id: plugin.video.new
# Addon Provider: Mr New

import pyxbmct
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.dialogs import themecontrol
from resources.lib.modules import control


class CacheDialog(pyxbmct.BlankDialogWindow):
    def __init__(self):
        super(CacheDialog, self).__init__()
        self.setGeometry(650, 366, 20, 60)

        self.colors = themecontrol.ThemeColors()

        self.Background = pyxbmct.Image(themecontrol.bg_mdialog)
        self.placeControl(self.Background, 0, 0, rowspan=20, columnspan=60)

        self.TraktIcon = pyxbmct.Image(themecontrol.trakt_icon)
        self.placeControl(self.TraktIcon, 1, 1, rowspan=12, columnspan=20)


        self.traktCode = ''

        self.set_controls()
        self.set_navigation()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        '''
        Left Side Menu Top Section

        self.Section1 = pyxbmct.Label('[B]Cache Options[/B]',
                                      alignment=pyxbmct.ALIGN_LEFT, textColor=self.colors.mh_color)
        self.placeControl(self.Section1, 3, 1, columnspan=17)
        self.menu = pyxbmct.List(textColor=self.colors.mt_color)
        self.placeControl(self.menu, 4, 1, rowspan=8, columnspan=17)
        self.menu.addItems(['Base',
                            'Providers',
                            'Meta',
                            'Search',
                            'All'])
        '''
        self.CancelButton = pyxbmct.Button(
            'Cancel', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.CancelButton, 17, 26, rowspan=2, columnspan=9)
        self.connect(self.CancelButton, self.cancelAuth)

    def set_navigation(self):
        pass

    def update_view(self):
        pass

    def cancelAuth(self):
        self.traktCode = ''
        self.close()
        pass


def load():
    dialog = CacheDialog()
    dialog.doModal()
    del dialog
