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

import re
import os
import traceback
import webbrowser

import pyxbmct
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.dialogs import themecontrol
from resources.lib.modules import client, control, log_utils


PAIR_LIST = [
    ("openload", "https://olpair.com/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL29wZW5sb2FkLnBuZw=='),
    ("streamango", "https://streamango.com/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3N0cmVhbWFuZ28ucG5n'),
    ("streamcherry", "https://streamcherry.com/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3N0cmVhbWNoZXJyeS5wbmc='),
    ("the_video_me", "https://vev.io/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3ZldmlvLnBuZw=='),
    ("vid_up_io", "https://vidup.io/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3ZpZHVwLnBuZw=='),
    ("vshare", "https://vshare.eu/pair",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3ZzaGFyZWV1LnBuZw=='),
    ("flashx", "https://www.flashx.tv/?op=login&redirect=https://www.flashx.tv/pairing.php",
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL2ZsYXNoeC5wbmc=')]

AUTH_LIST = [
    ("trakt", 'RunPlugin(plugin://plugin.video.new/?action=authTrakt)',
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3RyYWt0LnBuZw=='),
    ("real_debrid", 'RunPlugin(plugin://script.module.resolveurl/?mode=auth_rd)',
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3JkLnBuZw=='),
    ("premiumize_me", 'RunPlugin(plugin://script.module.resolveurl/?mode=auth_pm)',
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3ByZW1pdW1pemUucG5n'),
    ("alldebrid", 'RunPlugin(plugin://script.module.resolveurl/?mode=auth_ad)',
     'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3RoZXJlYWxhdHJlaWRlcy9hdHJlaWRlc2V4dHJhcy9tYXN0ZXIvYXJ0d29yay9wYWlyaW5nL3JkLnBuZw==')]


class NewsDialog(pyxbmct.BlankDialogWindow):
    def __init__(self):
        super(NewsDialog, self).__init__()
        self.setGeometry(800, 450, 20, 60)

        self.colors = themecontrol.ThemeColors()
        self.open_browser = control.setting('browser.pair')
        if self.open_browser == '' or self.open_browser == 'true':
            self.open_browser = True
        else:
            self.open_browser = False

        self.Background = pyxbmct.Image(themecontrol.bg_news)
        self.placeControl(self.Background, 0, 0, rowspan=20, columnspan=60)

        self.set_controls()
        self.set_navigation()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

        self.video = None

    def set_controls(self):
        '''
        Left Side Menu Top Section
        '''
        self.MenuSection = pyxbmct.Label(
            '[B]Tool Menu[/B]', alignment=pyxbmct.ALIGN_LEFT, textColor=self.colors.mh_color)
        self.placeControl(self.MenuSection, 3, 1, columnspan=17)
        self.menu = pyxbmct.List(textColor=self.colors.mt_color)
        self.placeControl(self.menu, 4, 1, rowspan=8, columnspan=17)
        self.menu.addItems(['Pairing', 'Authorize'])

        '''
        Primary buttons in left menu
        '''
        self.CloseButton = pyxbmct.Button(
            'Close', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.CloseButton, 17, 10, rowspan=2, columnspan=8)
        self.connect(self.CloseButton, self.close)

        self.OpenButton = pyxbmct.RadioButton(
            'Open in Browser', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa')
        self.placeControl(self.OpenButton, 12, 1, rowspan=2, columnspan=17)
        self.OpenButton.setSelected(self.open_browser)
        self.connect(self.OpenButton, self.toggle)

        '''
        Right Side, to display stuff for the above menu items
        '''
        self.pairingheader = '[B]Pairing Tool[/B]'
        self.Header = pyxbmct.Label(self.pairingheader, alignment=pyxbmct.ALIGN_CENTER, textColor=self.colors.dh_color)
        self.placeControl(self.Header, 2, 20, rowspan=1, columnspan=40)
        self.pairMenu = pyxbmct.List(textColor=self.colors.mt_color, _imageWidth=50, _imageHeight=50)
        self.placeControl(self.pairMenu, 3, 21, rowspan=20, columnspan=30)
        pairItems = []
        for item in PAIR_LIST:
            the_title = 'Pair for %s' % (item[0].replace('_', ' ').capitalize())
            the_item = control.item(label=the_title)
            the_icon = item[2].decode('base64')
            the_item.setArt({'icon': the_icon, 'thumb': the_icon})
            pairItems.append(the_item)
        self.pairMenu.addItems(pairItems)
        self.connect(self.pairMenu, self.pairHandler)

        self.authMenu = pyxbmct.List(textColor=self.colors.mt_color, _imageWidth=50, _imageHeight=50)
        self.placeControl(self.authMenu, 3, 21, rowspan=20, columnspan=30)
        self.authMenu.setVisible(False)
        authItems = []
        for item in AUTH_LIST:
            the_title = 'Authorize %s' % (item[0].replace('_', ' ').capitalize())
            the_item = control.item(label=the_title)
            the_icon = item[2].decode('base64')
            the_item.setArt({'icon': the_icon, 'thumb': the_icon})
            authItems.append(the_item)
        self.authMenu.addItems(authItems)
        self.connect(self.authMenu, self.authHandler)

    def set_navigation(self):
        self.menu.controlUp(self.CloseButton)
        self.menu.controlDown(self.OpenButton)
        self.menu.controlRight(self.pairMenu)
        self.pairMenu.controlLeft(self.menu)
        self.authMenu.controlLeft(self.menu)
        self.OpenButton.controlUp(self.menu)
        self.OpenButton.controlDown(self.CloseButton)
        self.CloseButton.controlUp(self.OpenButton)
        self.CloseButton.controlDown(self.menu)

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
                selection = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
                if selection == 'Pairing':
                    self.Header.setLabel(self.pairingheader)
                    self.pairMenu.setVisible(True)
                    self.authMenu.setVisible(False)
                    self.menu.controlRight(self.pairMenu)
                elif selection == 'Authorize':
                    self.Header.setLabel('[B]Authorize New[/B]', textColor=self.colors.dh_color)
                    self.authMenu.setVisible(True)
                    self.pairMenu.setVisible(False)
                    self.menu.controlRight(self.authMenu)
            else:
                pass
        except (RuntimeError, SystemError):
            pass

    def toggle(self):
        if self.OpenButton.isSelected():
            self.open_browser = True
            control.setSetting('browser.pair', 'true')
        else:
            self.open_browser = False
            control.setSetting('browser.pair', 'false')

    def pairHandler(self):
        selection = self.pairMenu.getListItem(self.pairMenu.getSelectedPosition()).getLabel()
        self.close()

        pair_item = re.sub('\[.*?]', '', selection).replace('Pair for ', '').replace(' ', '_').lower()
        for item in PAIR_LIST:
            if str(item[0]) == pair_item:
                site = item[1]
                site_name = item[0].replace('_', ' ').capitalize()
                break

        if self.open_browser:
            check_os = platform()
            if check_os == 'android':
                xbmc.executebuiltin('StartAndroidActivity(,android.intent.action.VIEW,,%s)' % (site))
            elif check_os == 'osx':
                os.system("open " + site)
            else:
                webbrowser.open(site)
        else:
            try:
                from resources.lib.dialogs import ok
                ok.load('%s Stream Authorization' % (site_name), 'Using a device on your network, visit the link below to   authorize streams:', site)
            except Exception:
                failure = traceback.format_exc()
                log_utils.log('Pairing - Exception: \n' + str(failure))
                return

    def authHandler(self):
        selection = self.authMenu.getListItem(self.authMenu.getSelectedPosition()).getLabel()
        self.close()

        auth_item = re.sub('\[.*?]', '', selection).replace('Authorize ', '').replace(' ', '_').lower()
        func = None
        for item in AUTH_LIST:
            if str(item[0]) == auth_item:
                func = item[1]
                break

        if func is not None:
            xbmc.executebuiltin(func)


def load():
    dialog = NewsDialog()
    dialog.doModal()
    del dialog


def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'
