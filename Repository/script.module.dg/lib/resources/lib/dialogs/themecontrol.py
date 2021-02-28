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

import os
import xml.etree.ElementTree as ET

import xbmcaddon

from resources.lib.modules import control

artPath = control.artPath()
_addon = xbmcaddon.Addon(id='plugin.video.new')
addonname = _addon.getAddonInfo('name')

bg_news = os.path.join(artPath, 'newsbg.png')
bg_mid = os.path.join(artPath, 'bg_mid.png')
bg_ok = os.path.join(artPath, 'okbg.png')
bg_mdialog = os.path.join(artPath, 'mdialogbg.png')
btn_focus = os.path.join(artPath, 'onfocus.png')
btn_nofocus = os.path.join(artPath, 'onnofocus.png')
trakt_icon = os.path.join(artPath, 'trakticon.png')

class ThemeColors():
    def __init__(self):
        self.colors()

    def colors(self):
        tree = ET.parse(os.path.join(artPath, 'colors.xml'))
        root = tree.getroot()
        for item in root.findall('color'):
                self.dh_color = item.find('dialogheader').text
                self.mh_color = item.find('menuheader').text
                self.mt_color = item.find('menutext').text
                self.link_color = item.find('link').text
