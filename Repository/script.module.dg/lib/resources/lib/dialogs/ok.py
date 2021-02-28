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
from resources.lib.modules import client


class OkDialog(pyxbmct.BlankDialogWindow):
    def __init__(self):
        super(OkDialog, self).__init__()
        self.setGeometry(650, 250, 20, 60)

        self.colors = themecontrol.ThemeColors()

        self.Background = pyxbmct.Image(themecontrol.bg_ok)
        self.placeControl(self.Background, 0, 0, rowspan=20, columnspan=60)

        self.set_controls()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def setInfo(self, header='', msg='', url=None):
        '''
        Header Text Placement
        '''
        self.header_text = '[B]%s[/B]' % (header)
        self.Header = pyxbmct.Label(self.header_text, alignment=pyxbmct.ALIGN_CENTER, textColor=self.colors.dh_color)

        '''
        58 characters per line
        '''
        lines = ''
        temp = msg.split('\n')
        for temp_line in temp:
            for chunk in self.chunkybitch(temp_line, 58):
                lines += chunk.strip() + '\n'
        if url is not None:
            url = '[B][COLOR %s]%s[/COLOR][/B]' % (self.colors.link_color, url)
            lines += url
        self.placeControl(self.Header, 2, 0, rowspan=2, columnspan=60)
        self.Description = pyxbmct.Label(lines)
        self.placeControl(self.Description, 4, 4, rowspan=8, columnspan=53)

    def set_controls(self):
        self.OKButton = pyxbmct.Button(
            'Close', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.OKButton, 14, 25, rowspan=4, columnspan=10)
        self.connect(self.OKButton, self.close)
        self.setFocus(self.OKButton)

    def chunkybitch(self, s, n):
        for start in range(0, len(s), n):
            if '[B][C' in s[start:start+n]:
                n = n+31
            yield s[start:start+n]


def load(header='', msg='', url=None):
    dialog = OkDialog()
    dialog.setInfo(header, msg, url)
    dialog.doModal()
    del dialog
