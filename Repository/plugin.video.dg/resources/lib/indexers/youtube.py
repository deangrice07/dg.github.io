# -*- coding: UTF-8 -*-


# Addon Name: Mirrorv2
# Addon id: plugin.video.mirrorv2
# Addon Provider: Cy4Root

import sys
from resources.lib.modules import control
from resources.lib.modules import youtube_menu

thishandle = int(sys.argv[1])

class yt_index:  # initializes as Kids Corner, functions can override based on action and subid.
    def __init__(self):
        self.action = 'kidscorner'
        self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F796F75747562652F'.decode('hex')
        self.mainmenu = '%sknmain.txt' % (self.base_url)
        self.submenu  = '%s/%s.txt'
        self.default_icon   = '%s/icons/icon.png'
        self.default_fanart = '%s/icons/fanart.jpg'


    def init_vars(self, action):
        try:
            if action == 'fitness': 
                self.action   = 'fitness'
                self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F796F75747562652F'.decode('hex')
                self.mainmenu = '%sfzmain.txt' % (self.base_url)

	    elif action == 'youtube':
                self.action   = 'youtube'
                self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F796F75747562652F'.decode('hex')
                self.mainmenu = '%sytmain.txt' % (self.base_url)

	    elif action == 'legends':
                self.action   = 'legends'
                self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F6C6567656E64732F'.decode('hex')
                self.mainmenu = '%sihmain.txt' % (self.base_url)

	    elif action == 'kidscorner':
		self.action = 'kidscorner'
        	self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F796F75747562652F'.decode('hex')
        	self.mainmenu = '%sknmain.txt' % (self.base_url)

       	    elif action == 'mytube':
		self.action = 'mytube'
        	self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F796F75747562652F'.decode('hex')
        	self.mainmenu = '%sytmainmy.txt' % (self.base_url)

            elif action == 'tvReviews':
                self.action   = 'tvReviews'
                self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F746865637269746963732F'.decode('hex')
                self.mainmenu = '%stelevision.txt' % (self.base_url)

            elif action == 'movieReviews':
                self.action   = 'movieReviews'
                self.base_url = '68747470733A2F2F7261772E67697468756275736572636F6E74656E742E636F6D2F64656D6F6E2D6269742F786D6C2D6D61737465722F6D61737465722F746865637269746963732F'.decode('hex')
                self.mainmenu = '%smovies.txt' % (self.base_url)
            self.submenu = self.submenu % (self.base_url, '%s')
            self.default_icon = self.default_icon % (self.base_url)
            self.default_fanart = self.default_fanart % (self.base_url)
        except:
            pass


    def root(self, action):
        try:
            self.init_vars(action)
            menuItems = youtube_menu.youtube_menu().processMenuFile(self.mainmenu)
            for name, section, searchid, subid, playlistid, channelid, videoid, iconimage, fanart, description in menuItems:
                if not subid == 'false':  # Means this item points to a submenu
                    youtube_menu.youtube_menu().addMenuItem(name, self.action, subid, iconimage, fanart, description, True)
                elif not searchid == 'false':  # Means this is a search term
                    youtube_menu.youtube_menu().addSearchItem(name, searchid, iconimage, fanart)
                elif not videoid == 'false':  # Means this is a video id entry
                    youtube_menu.youtube_menu().addVideoItem(name, videoid, iconimage, fanart)
                elif not channelid == 'false':  # Means this is a channel id entry
                    youtube_menu.youtube_menu().addChannelItem(name, channelid, iconimage, fanart)
                elif not playlistid == 'false':  # Means this is a playlist id entry
                    youtube_menu.youtube_menu().addPlaylistItem(name, playlistid, iconimage, fanart)
                elif not section == 'false':  # Means this is a section placeholder/info line
                    youtube_menu.youtube_menu().addSectionItem(name, self.default_icon, self.default_fanart)
            self.endDirectory()
        except:
            pass


    def get(self, action, subid):
        try:
            self.init_vars(action)
            thisMenuFile = self.submenu % (subid)
            menuItems = youtube_menu.youtube_menu().processMenuFile(thisMenuFile)
            for name, section, searchid, subid, playlistid, channelid, videoid, iconimage, fanart, description in menuItems:
                if not subid == 'false':  # Means this item points to a submenu
                    youtube_menu.youtube_menu().addMenuItem(name, self.action, subid, iconimage, fanart, description, True)
                elif not searchid == 'false':  # Means this is a search term
                    youtube_menu.youtube_menu().addSearchItem(name, searchid, iconimage, fanart)
                elif not videoid == 'false':  # Means this is a video id entry
                    youtube_menu.youtube_menu().addVideoItem(name, videoid, iconimage, fanart)
                elif not channelid == 'false':  # Means this is a channel id entry
                    youtube_menu.youtube_menu().addChannelItem(name, channelid, iconimage, fanart)
                elif not playlistid == 'false':  # Means this is a playlist id entry
                    youtube_menu.youtube_menu().addPlaylistItem(name, playlistid, iconimage, fanart)
                elif not section == 'false':  # Means this is a section placeholder/info line
                    youtube_menu.youtube_menu().addSectionItem(name, self.default_icon, self.default_fanart)
            self.endDirectory()
        except:
            pass


    def endDirectory(self):
        control.directory(thishandle, cacheToDisc=True)


