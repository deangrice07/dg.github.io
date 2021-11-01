# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import xbmc
from resources.lib.modules.control import dialog, getHighlightColor, sleep, condVisibility
from resources.lib.windows.base import BaseDialog

monitor = xbmc.Monitor()


class TraktMovieProgressManagerXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		super(TraktMovieProgressManagerXML, self).__init__(self, args)
		self.window_id = 2050
		self.results = kwargs.get('results')
		self.total_results = str(len(self.results))
		self.selected_items = []
		self.make_items()
		self.set_properties()
		self.hasVideo = False

	def onInit(self):
		super(TraktMovieProgressManagerXML, self).onInit()
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		return self.selected_items

	# def onClick(self, controlID):
		# from resources.lib.modules import log_utils
		# log_utils.log('controlID=%s' % controlID)

	def onAction(self, action):
		try:
			if action in self.selection_actions:
				focus_id = self.getFocusId()
				if focus_id == 2050: # listItems
					position = self.get_position(self.window_id)
					chosen_listitem = self.item_list[position]
					imdb = chosen_listitem.getProperty('dg.imdb')
					if chosen_listitem.getProperty('dg.isSelected') == 'true':
						chosen_listitem.setProperty('dg.isSelected', '')
						if imdb in self.selected_items: self.selected_items.remove(imdb)
					else:
						chosen_listitem.setProperty('dg.isSelected', 'true')
						self.selected_items.append(imdb)
				elif focus_id == 2051: # OK Button
					self.close()
				elif focus_id == 2052: # Cancel Button
					self.selected_items = None
					self.close()
				elif focus_id == 2053: # Select All Button
					for item in self.item_list:
						item.setProperty('dg.isSelected', 'true')
				elif focus_id == 2045: # Stop Trailer Playback Button
					self.execute_code('PlayerControl(Stop)')
					sleep(500)
					self.setFocusId(self.window_id)

			elif action in self.context_actions:
				cm = []
				chosen_listitem = self.item_list[self.get_position(self.window_id)]
				# media_type = chosen_listitem.getProperty('dg.media_type')
				source_trailer = chosen_listitem.getProperty('dg.trailer')
				if not source_trailer:
					from resources.lib.modules import trailer
					source_trailer = trailer.Trailer().worker('movie', chosen_listitem.getProperty('dg.title'), chosen_listitem.getProperty('dg.year'), None, chosen_listitem.getProperty('dg.imdb'))

				if source_trailer: cm += [('[B]Play Trailer[/B]', 'playTrailer')]
				chosen_cm_item = dialog.contextmenu([i[0] for i in cm])
				if chosen_cm_item == -1: return
				cm_action = cm[chosen_cm_item][1]

				if cm_action == 'playTrailer':
					self.execute_code('PlayMedia(%s, 1)' % source_trailer)
					total_sleep = 0
					while True:
						sleep(500)
						total_sleep += 500
						self.hasVideo = condVisibility('Player.HasVideo')
						if self.hasVideo or total_sleep >= 10000: break
					if self.hasVideo:
						self.setFocusId(2045)
						while (condVisibility('Player.HasVideo') and not monitor.abortRequested()):
							self.setProgressBar()
							sleep(1000)
						self.hasVideo = False
						self.progressBarReset()
						self.setFocusId(self.window_id)
					else: self.setFocusId(self.window_id)

			elif action in self.closing_actions:
				self.selected_items = None
				if self.hasVideo: self.execute_code('PlayerControl(Stop)')
				else: self.close()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			self.close()

	def setProgressBar(self):
		try: progress_bar = self.getControlProgress(2046)
		except: progress_bar = None
		if progress_bar is not None:
			progress_bar.setPercent(self.calculate_percent())

	def calculate_percent(self):
		return (xbmc.Player().getTime() / float(xbmc.Player().getTotalTime())) * 100

	def progressBarReset(self):
		try: progress_bar = self.getControlProgress(2046)
		except: progress_bar = None
		if progress_bar is not None:
			progress_bar.setPercent(0)

	def make_items(self):
		def builder():
			for count, item in enumerate(self.results, 1):
				try:
					listitem = self.make_listitem()
					listitem.setProperty('dg.title', item.get('title'))
					listitem.setProperty('dg.year', str(item.get('year')))
					# labelProgress = str(round(float(item['progress'] * 100), 1)) + '%'
					labelProgress = str(round(float(item['progress']), 1)) + '%'
					listitem.setProperty('dg.progress', '[' + labelProgress + ']')
					listitem.setProperty('dg.isSelected', '')
					listitem.setProperty('dg.imdb', item.get('imdb'))
					# listitem.setProperty('dg.tmdb', item.get('tmdb'))
					listitem.setProperty('dg.rating', str(round(float(item.get('rating')), 1)))
					listitem.setProperty('dg.trailer', item.get('trailer'))
					listitem.setProperty('dg.studio', item.get('studio'))
					listitem.setProperty('dg.genre', item.get('genre', ''))
					listitem.setProperty('dg.duration', str(item.get('duration')))
					listitem.setProperty('dg.mpaa', item.get('mpaa') or 'NA')
					listitem.setProperty('dg.plot', item.get('plot'))
					listitem.setProperty('dg.poster', item.get('poster', ''))
					listitem.setProperty('dg.clearlogo', item.get('clearlogo', ''))
					listitem.setProperty('dg.count', '%02d.)' % count)
					yield listitem
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
		try:
			self.item_list = list(builder())
			self.total_results = str(len(self.item_list))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def set_properties(self):
		try:
			self.setProperty('dg.total_results', self.total_results)
			self.setProperty('dg.highlight.color', getHighlightColor())
		except:
			from resources.lib.modules import log_utils
			log_utils.error()