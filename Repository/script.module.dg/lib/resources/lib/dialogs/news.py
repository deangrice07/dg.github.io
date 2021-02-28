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
from resources.lib.modules import client, control


#newsfile = 'https://raw.githubusercontent.com/Mr-invisibles/test/master/plugin.video.invisible/newsinfo.txt'
#changesfile =
#approvedfile =
#paypalfile =
#bugsfile =
#scraperfile =
#rdfile =
#torrentfile =

#scrapervid = 'aHR0cHM6Ly9naXRodWIuY29tL211YWRkaWJ0dHYvYXJ0d29yay9ibG9iL21hc3Rlci92aWRlb3Mvc2NyYXBlcnMtYW5kLWZpbHRlcnMubXA0P3Jhdz10cnVl'
#rdvid = 'aHR0cHM6Ly9naXRodWIuY29tL211YWRkaWJ0dHYvYXJ0d29yay9ibG9iL21hc3Rlci92aWRlb3MvcmVhbC1kZWJyaWQubXA0P3Jhdz10cnVl'
#torrentvid = 'aHR0cHM6Ly9naXRodWIuY29tL211YWRkaWJ0dHYvYXJ0d29yay9ibG9iL21hc3Rlci92aWRlb3MvdHN1cHBvcnQubXA0P3Jhdz10cnVl'


#class NewsDialog(pyxbmct.BlankDialogWindow):
#    def __init__(self):
#        super(NewsDialog, self).__init__()
#        self.setGeometry(800, 450, 20, 60)

#        self.colors = themecontrol.ThemeColors()

#        self.Background = pyxbmct.Image(themecontrol.bg_news)
#        self.placeControl(self.Background, 0, 0, rowspan=20, columnspan=60)

#        self.news = self.getDialogText(newsfile)
#        self.changes = self.getDialogText(changesfile)
#        self.approved = self.getDialogText(approvedfile)
#        self.paypal = self.getDialogText(paypalfile)
#        self.scrapers = self.getDialogText(scraperfile)
#        self.rd = self.getDialogText(rdfile)
#        self.torrents = self.getDialogText(torrentfile)
#        self.set_controls()
#        self.set_navigation()
#        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

#        self.video = None

    def set_controls(self):
        '''
        Left Side Menu Top Section
        '''
        self.Section1 = pyxbmct.Label('[B]Addon Information[/B]',
                                      alignment=pyxbmct.ALIGN_LEFT, textColor=self.colors.mh_color)
        self.placeControl(self.Section1, 3, 1, columnspan=17)
        self.menu = pyxbmct.List(textColor=self.colors.mt_color)
        self.placeControl(self.menu, 4, 1, rowspan=8, columnspan=17)
        self.menu.addItems(['News',
                            'Changes',
                            'Builds',
                            'Paypal',
                            'Bug Reports'])
        '''
        Left Side Menu Bottom Section, currently unused
        '''
        self.Section2 = pyxbmct.Label('[B]Tips and Tricks[/B]',
                                      alignment=pyxbmct.ALIGN_LEFT, textColor=self.colors.mh_color)
        self.placeControl(self.Section2, 11, 1, rowspan=4, columnspan=17)
        self.menu2 = pyxbmct.List(textColor=self.colors.mt_color)
        self.placeControl(self.menu2, 12, 1, rowspan=12, columnspan=17)
        self.menu2.addItems(['Scraper Tips',
                             'Real Debrid',
                             'Torrents'])

        self.CloseButton = pyxbmct.Button(
            'Close', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.CloseButton, 17, 10, rowspan=2, columnspan=8)
        self.connect(self.CloseButton, self.close)
        '''
        Right Side, to display stuff for the above menu items
        '''
        self.newsheader = '[B]Latest News[/B]'
        self.Header = pyxbmct.Label(self.newsheader, alignment=pyxbmct.ALIGN_CENTER, textColor=self.colors.dh_color)
        self.placeControl(self.Header, 2, 20, rowspan=1, columnspan=40)
        self.Description = pyxbmct.Label(self.news)
        self.placeControl(self.Description, 3, 21, rowspan=20, columnspan=40)

        self.RDLink = pyxbmct.Label('Referral Debrid Link: ' + str(get_rd_link()))
        self.placeControl(self.RDLink, 17, 21, rowspan=2, columnspan=30)
        self.RDLink.setVisible(False)

        self.WatchButton = pyxbmct.Button(
            'Watch', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.WatchButton, 15, 36, rowspan=2, columnspan=8)
        self.WatchButton.setVisible(False)
        self.connect(self.WatchButton, self.watchVideo)

        self.BugForm = pyxbmct.Edit('', _alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.BugForm, 8, 24, 2, 31)
        self.BugForm.setVisible(False)

        self.SubmitButton = pyxbmct.Button(
            'Submit', textColor='0xFFFFFFFF', shadowColor='0xFF000000', focusedColor='0xFFbababa',
            focusTexture=themecontrol.btn_focus, noFocusTexture=themecontrol.btn_nofocus)
        self.placeControl(self.SubmitButton, 15, 36, rowspan=2, columnspan=8)
        self.SubmitButton.setVisible(False)
        self.connect(self.SubmitButton, self.submitForm)

    def set_navigation(self):
        self.menu.controlUp(self.menu2)
        self.menu.controlDown(self.menu2)
        self.menu.controlRight(self.BugForm)
        self.BugForm.controlLeft(self.menu)
        self.BugForm.controlDown(self.SubmitButton)
        self.SubmitButton.controlUp(self.BugForm)
        self.SubmitButton.controlLeft(self.menu)
        self.menu2.controlUp(self.menu)
        self.menu2.controlDown(self.CloseButton)
        self.menu2.controlRight(self.WatchButton)
        self.CloseButton.controlUp(self.menu2)
        self.CloseButton.controlDown(self.menu)
        self.WatchButton.controlLeft(self.menu2)

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
                self.SubmitButton.setVisible(False)
                self.BugForm.setVisible(False)
                self.WatchButton.setVisible(False)
                self.RDLink.setVisible(False)
                self.video = None
                selection = self.menu.getListItem(self.menu.getSelectedPosition()).getLabel()
                if selection == 'News':
                    self.Header.setLabel(self.newsheader)
                    self.Description.setLabel(self.news)
                elif selection == 'Changes':
                    self.Header.setLabel('[B]Latest Changes[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.changes)
                elif selection == 'Builds':
                    self.Header.setLabel('[B]Approved Builds[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.approved)
                elif selection == 'Paypal':
                    self.Header.setLabel('[B]Paypal[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.paypal)
                elif selection == 'Bug Reports':
                    self.Header.setLabel('[B]Bug Reports[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel('If you think you found a bug, broken scraper, bad\nresults, and so on then please let us know below!')
                    self.SubmitButton.setVisible(True)
                    self.BugForm.setVisible(True)
            elif self.getFocus() == self.menu2:
                self.SubmitButton.setVisible(False)
                self.BugForm.setVisible(False)
                selection = self.menu2.getListItem(self.menu2.getSelectedPosition()).getLabel()
                self.WatchButton.setVisible(True)
                if selection == 'Scraper Tips':
                    self.Header.setLabel('[B]Scraper Tips[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.scrapers)
                    self.video = scrapervid
                    self.RDLink.setVisible(False)
                elif selection == 'Real Debrid':
                    self.Header.setLabel('[B]Real Debrid[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.rd)
                    self.video = rdvid
                    self.RDLink.setVisible(True)
                elif selection == 'Torrents':
                    self.Header.setLabel('[B]Torrents in New[/B]', textColor=self.colors.dh_color)
                    self.Description.setLabel(self.torrents)
                    self.video = torrentvid
                    self.RDLink.setVisible(False)
            else:
                pass
        except (RuntimeError, SystemError):
            pass

    def watchVideo(self):
        self.close()
        control.idle()
        # Kernal errors from within YouTube after displaying path details (so crash is permission based?) in Kodi 18. Need to find a valid fix
        # Have tried resolvedUrl but no valid handle due to custom GUI. Executing only causes crash or nothing at all (tried trailer url for
        # new default.py and just fails)
        control.execute('PlayMedia("%s")' % (self.video.decode('base64')))

    def submitForm(self):
        reportText = self.BugForm.getText()
        self.close()
        from resources.lib.modules import webform
        result = webform.webform().bug_report('New', reportText)
        if result is None:
            # Wait before submitting another report you fuckin spammer
            xbmc.executebuiltin("XBMC.Notification(%s, %s, %s, %s)" % ('New Bug Report', 'Wait Before Next Submission', 4000, control.addonIcon()))
        elif result is False:
            # Failed to send. Site timed out or is down. Ya'll suck
            xbmc.executebuiltin("XBMC.Notification(%s, %s, %s, %s)" % ('New Bug Report', 'Submission Failed', 4000, control.addonIcon()))
        elif result is True:
            # Bug Report worked, FUCK YEAH!
            xbmc.executebuiltin("XBMC.Notification(%s, %s, %s, %s)" % ('New Bug Report', 'Bug Report Completed', 4000, control.addonIcon()))

    def getDialogText(self, url):
        try:
            message = open_my_url(url)

            if message is None:
                return 'Nothing today! Blame CNN'
            if '[link]' in message:
                tcolor = '[COLOR %s]' % (self.colors.link_color)
                message = message.replace('[link]', tcolor).replace('[/link]', '[/COLOR]')
            return message
        except Exception:
            return 'Nothing today! Blame CNN'


def get_rd_link():
    import random
    result = random.choice(['aHR0cDovL2JpdC5seS8yRkRlQ1Rx', 'aHR0cDovL2JpdC5seS8yUjJMZFRD',
                            'aHR0cDovL2JpdC5seS8yRkRlQ1Rx'])
    return result.decode('base64')


def open_my_url(url):
    try:
        response = client.request(url)
        return response
    except Exception:
        return None


#def load():
#    dialog = NewsDialog()
#    dialog.doModal()
#    del dialog
