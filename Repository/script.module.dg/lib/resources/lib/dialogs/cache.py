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
        self.setGeometry(800, 450, 20, 60)

        self.colors = themecontrol.ThemeColors()

        self.Background = pyxbmct.Image(themecontrol.bg_news)
        self.placeControl(self.Background, 0, 0, rowspan=20, columnspan=60)

        self.cacheType = 'base'

        self.set_controls()
        self.set_navigation()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        '''
        Left Side Menu Top Section
        '''
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

        self.CloseButton = pyxbmct.Button(
            'Close', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.CloseButton, 17, 10, rowspan=2, columnspan=8)
        self.connect(self.CloseButton, self.close)

        self.ClearButton = pyxbmct.Button(
            'Clear', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.ClearButton, 15, 36, rowspan=2, columnspan=8)
        self.connect(self.ClearButton, self.clearCache)

        '''
        Right Side, to display stuff for the above menu items
        '''
        self.cacheheader = '[B]Clear Base Cache[/B]'
        self.Header = pyxbmct.Label(self.cacheheader, alignment=pyxbmct.ALIGN_CENTER, textColor=self.colors.dh_color)
        self.placeControl(self.Header, 2, 20, rowspan=1, columnspan=40)
        self.Description = pyxbmct.Label(control.lang(32648).encode('utf-8'))
        self.placeControl(self.Description, 3, 21, rowspan=20, columnspan=40)

    def set_navigation(self):
        self.menu.controlUp(self.CloseButton)
        self.menu.controlDown(self.CloseButton)
        self.menu.controlRight(self.ClearButton)
        self.CloseButton.controlUp(self.menu)
        self.CloseButton.controlDown(self.menu)
        self.CloseButton.controlRight(self.ClearButton)
        self.ClearButton.controlLeft(self.menu)

        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_UP,
             pyxbmct.ACTION_MOUSE_MOVE],
            self.update_view)
        # Set initial focus
        self.setFocus(self.menu)

    def update_view(self):
        try:
            if self.getFocus() == self.menu:
                self.video = None
                selection = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
                if selection == 'Base':
                    self.Header.setLabel(self.cacheheader)
                    self.Description.setLabel(control.lang(32648).encode('utf-8'))
                    self.cacheType = 'base'
                elif selection == 'Providers':
                    self.Header.setLabel('[B]Clear Provider Cache[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(control.lang(32649).encode('utf-8'))
                    self.cacheType = 'providers'
                elif selection == 'Meta':
                    self.Header.setLabel('[B]Clear Metadata Cache[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(control.lang(32650).encode('utf-8'))
                    self.cacheType = 'meta'
                elif selection == 'Search':
                    self.Header.setLabel('[B]Clear Search History[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(control.lang(32651).encode('utf-8'))
                    self.cacheType = 'search'
                elif selection == 'All':
                    self.Header.setLabel('[B]Clear All Cache[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(control.lang(32652).encode('utf-8'))
                    self.cacheType = 'all'
            else:
                pass
        except (RuntimeError, SystemError):
            pass

    def clearCache(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes:
            return
        self.close()

        from resources.lib.modules import cache
        if self.cacheType == 'base':
            cache.cache_clear()
        elif self.cacheType == 'providers':
            cache.cache_clear_providers()
        elif self.cacheType == 'meta':
            cache.cache_clear_meta()
        elif self.cacheType == 'search':
            cache.cache_clear_search()
        elif self.cacheType == 'all':
            cache.cache_clear_all()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')


def load():
    dialog = CacheDialog()
    dialog.doModal()
    del dialog
