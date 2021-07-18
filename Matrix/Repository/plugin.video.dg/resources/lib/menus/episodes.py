# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime, timedelta
from json import dumps as jsdumps, loads as jsloads
import re
from sys import argv
from urllib.parse import quote_plus, urlencode, parse_qsl, urlparse, urlsplit
from resources.lib.database import cache
from resources.lib.indexers import tmdb as tmdb_indexer, fanarttv
from resources.lib.modules import cleangenre
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules.playcount import getTVShowIndicators, getEpisodeOverlay, getShowCount
from resources.lib.modules import tools
from resources.lib.modules import trakt
from resources.lib.modules import views
from resources.lib.modules import workers


class Episodes:
	def __init__(self, type='show', notifications=True):
		self.count = control.setting('page.item.limit')
		self.list = []
		self.threads = []
		self.type = type
		self.lang = control.apiLanguage()['tmdb']
		self.notifications = notifications
		self.disable_fanarttv = control.setting('disable.fanarttv') == 'true'
		self.date_time = datetime.now()
		self.today_date = (self.date_time).strftime('%Y-%m-%d')

		self.trakt_user = control.setting('trakt.user').strip()
		self.traktCredentials = trakt.getTraktCredentialsInfo()
		self.trakt_link = 'https://api.trakt.tv'
		self.traktlist_link = 'https://api.trakt.tv/users/%s/lists/%s/items/episodes'
		self.traktlists_link = 'https://api.trakt.tv/users/me/lists'
		self.traktlikedlists_link = 'https://api.trakt.tv/users/likes/lists?limit=1000000'
		self.traktwatchlist_link = 'https://api.trakt.tv/users/me/watchlist/episodes'
		self.trakthistory_link = 'https://api.trakt.tv/users/me/history/shows?limit=%s&page=1' % self.count
		self.progress_link = 'https://api.trakt.tv/users/me/watched/shows'
		self.hiddenprogress_link = 'https://api.trakt.tv/users/hidden/progress_watched?limit=1000&type=show'
		self.mycalendar_link = 'https://api.trakt.tv/calendars/my/shows/date[30]/32/'
		self.traktunfinished_link = 'https://api.trakt.tv/sync/playback/episodes?limit=40'

		self.tvmaze_link = 'https://api.tvmaze.com'
		self.added_link = 'https://api.tvmaze.com/schedule'
		self.calendar_link = 'https://api.tvmaze.com/schedule?date=%s'

		self.showunaired = control.setting('showunaired') == 'true'
		self.unairedcolor = control.getColor(control.setting('unaired.identify'))
		self.showspecials = control.setting('tv.specials') == 'true'
		self.highlight_color = control.getColor(control.setting('highlight.color'))

	def get(self, tvshowtitle, year, imdb, tmdb, tvdb, meta, season=None, episode=None, idx=True, create_directory=True):
		self.list = []
		try:
			if season is None and episode is None: # for "flatten" setting
				def get_episodes(tvshowtitle, imdb, tmdb, tvdb, meta, season):
					episodes = cache.get(self.tmdb_list, 96, tvshowtitle, imdb, tmdb, tvdb, meta, season)
					all_episodes.extend(episodes)
				all_episodes = []
				threads = []
				if not isinstance(meta, dict): showSeasons = jsloads(meta)
				else: showSeasons = meta
				try:
					for i in showSeasons['seasons']:
						if not self.showspecials and i['season_number'] == 0: continue
						threads.append(workers.Thread(get_episodes, tvshowtitle, imdb, tmdb, tvdb, meta, i['season_number']))
					[i.start() for i in threads]
					[i.join() for i in threads]
					self.list = sorted(all_episodes, key=lambda k: (k['season'], k['episode']), reverse=False)
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
			elif season and episode: # for "trakt progress-non direct progress scrape" setting
				self.list = cache.get(self.tmdb_list, 96, tvshowtitle, imdb, tmdb, tvdb, meta, season)
				num = [x for x, y in enumerate(self.list) if y['season'] == int(season) and y['episode'] == int(episode)][-1]
				self.list = [y for x, y in enumerate(self.list) if x >= num]
			else: # normal full episode list
				self.list = cache.get(self.tmdb_list, 96, tvshowtitle, imdb, tmdb, tvdb, meta, season)
			if self.list is None: self.list = []
			if create_directory: self.episodeDirectory(self.list)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32326, message=33049)

	def unfinished(self, url):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			activity = trakt.getPausedActivity()
			if url == self.traktunfinished_link :
				try:
					if activity > cache.timeout(self.trakt_episodes_list, url, self.trakt_user, self.lang): raise Exception()
					self.list = cache.get(self.trakt_episodes_list, 720, url, self.trakt_user, self.lang)
				except:
					self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)
				if self.list is None: self.list = []
				self.list = sorted(self.list, key=lambda k: k['paused_at'], reverse=True)
				self.episodeDirectory(self.list, unfinished=True, next=False)
				return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32326, message=33049)

	def upcoming_progress(self, url):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			activity = trakt.getActivity()
			if self.trakt_link in url and url == self.progress_link:
				try:
					if activity > cache.timeout(self.trakt_progress_list, url, self.trakt_user, self.lang, True, True): raise Exception()
					self.list = cache.get(self.trakt_progress_list, 24, url, self.trakt_user, self.lang, direct)
				except:
					self.list = cache.get(self.trakt_progress_list, 0, url, self.trakt_user, self.lang, True, True)
				try:
					if not self.list: raise Exception()
					for i in range(len(self.list)):
						if 'premiered' not in self.list[i]: self.list[i]['premiered'] = ''
						if 'airtime' not in self.list[i]: self.list[i]['airtime'] = ''
					self.list = sorted(self.list, key=lambda k: (k['premiered'] if k['premiered'] else '3021-01-01', k['airtime'])) # "3021" date hack to force unknown premiered dates to bottom of list
				except: pass
			if self.list is None: self.list = []
			self.episodeDirectory(self.list, unfinished=False, next=False)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32326, message=33049)

	def calendar(self, url):
		self.list = []
		try:
			try: url = getattr(self, url + '_link')
			except: pass
			isTraktHistory = (url.split('&page=')[0] in self.trakthistory_link)
			if self.trakt_link in url and url == self.progress_link:
				direct = control.setting('tvshows.direct') == 'true'
				try:
					if trakt.getActivity() > cache.timeout(self.trakt_progress_list, url, self.trakt_user, self.lang, direct): raise Exception()
					self.list = cache.get(self.trakt_progress_list, 24, url, self.trakt_user, self.lang, direct)
				except:
					self.list = cache.get(self.trakt_progress_list, 0, url, self.trakt_user, self.lang, direct)
				self.sort(type='progress')
			elif self.trakt_link in url and url == self.mycalendar_link:
				self.list = cache.get(self.trakt_episodes_list, 0.3, url, self.trakt_user, self.lang)
				self.sort(type='calendar')
			elif isTraktHistory:
				try:
					if trakt.getActivity() > cache.timeout(self.trakt_episodes_list, url, self.trakt_user, self.lang): raise Exception()
					self.list = cache.get(self.trakt_episodes_list, 24, url, self.trakt_user, self.lang)
				except:
					self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)
				for i in range(len(self.list)): self.list[i]['traktHistory'] = True
				self.sort(type='progress')
			elif self.trakt_link in url and '/users/' in url:
				self.list = cache.get(self.trakt_episodes_list, 0.3, url, self.trakt_user, self.lang)
				self.sort(type='calendar')
			elif self.trakt_link in url: # I don't think this is used anymore
				self.list = cache.get(self.trakt_list, 1, url, self.trakt_user, True)
			elif self.tvmaze_link in url and url == self.added_link:
				urls = [i['url'] for i in self.calendars(idx=False)][:5]
				self.list = []
				for url in urls: self.list += cache.get(self.tvmaze_list, 720, url, True)
			elif self.tvmaze_link in url:
				self.list = cache.get(self.tvmaze_list, 1, url, False)
			if self.list is None: self.list = []
			hasNext = True if isTraktHistory else False
			self.episodeDirectory(self.list, unfinished=False, next=hasNext)
			return self.list
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			if not self.list:
				control.hide()
				if self.notifications: control.notification(title=32326, message=33049)

	def sort(self, type='shows'):
		try:
			if not self.list: return
			attribute = int(control.setting('sort.%s.type' % type))
			reverse = int(control.setting('sort.%s.order' % type)) == 1
			if attribute == 0: reverse = False # Sorting Order is not enabled when sort method is "Default"
			if attribute > 0:
				if attribute == 1:
					try: self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['tvshowtitle'].lower()), reverse=reverse)
					except: self.list = sorted(self.list, key=lambda k: k['title'].lower(), reverse=reverse)
				elif attribute == 2: self.list = sorted(self.list, key=lambda k: float(k['rating']), reverse=reverse)
				elif attribute == 3: self.list = sorted(self.list, key=lambda k: int(k['votes'].replace(',', '')), reverse=reverse)
				elif attribute == 4:
					for i in range(len(self.list)):
						if 'premiered' not in self.list[i]: self.list[i]['premiered'] = ''
					self.list = sorted(self.list, key=lambda k: k['premiered'], reverse=reverse)
				elif attribute == 5:
					for i in range(len(self.list)):
						if 'added' not in self.list[i]: self.list[i]['added'] = ''
					self.list = sorted(self.list, key=lambda k: k['added'], reverse=reverse)
				elif attribute == 6:
					for i in range(len(self.list)):
						if 'lastplayed' not in self.list[i]: self.list[i]['lastplayed'] = ''
					self.list = sorted(self.list, key=lambda k: k['lastplayed'], reverse=reverse)
			elif reverse:
				self.list = list(reversed(self.list))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def calendars(self, idx=True):
		m = control.lang(32060).split('|')
		try: months = [
					(m[0], 'January'), (m[1], 'February'), (m[2], 'March'), (m[3], 'April'), (m[4], 'May'), (m[5], 'June'), (m[6], 'July'),
					(m[7], 'August'), (m[8], 'September'), (m[9], 'October'), (m[10], 'November'), (m[11], 'December')]
		except: months = []
		d = control.lang(32061).split('|')
		try: days = [(d[0], 'Monday'), (d[1], 'Tuesday'), (d[2], 'Wednesday'), (d[3], 'Thursday'), (d[4], 'Friday'), (d[5], 'Saturday'), (d[6], 'Sunday')]
		except: days = []
		for i in range(0, 30):
			try:
				name = (self.date_time - timedelta(days=i))
				name = (control.lang(32062) % (name.strftime('%A'), name.strftime('%d %B')))
				for m in months: name = name.replace(m[1], m[0])
				for d in days: name = name.replace(d[1], d[0])
				url = self.calendar_link % (self.date_time - timedelta(days=i)).strftime('%Y-%m-%d')
				self.list.append({'name': name, 'url': url, 'image': 'calendar.png', 'icon': 'DefaultYear.png', 'action': 'calendar'})
			except: pass
		if idx: self.addDirectory(self.list)
		return self.list

	def userlists(self):
		userlists = []
		try:
			if not self.traktCredentials: raise Exception()
			activity = trakt.getActivity()
		except: pass
		try:
			if not self.traktCredentials: raise Exception()
			self.list = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
				userlists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
			except:
				userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
		except: pass
		try:
			if not self.traktCredentials: raise Exception()
			self.list = []
			try:
				if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
				userlists += cache.get(self.trakt_user_list, 720, self.traktlikedlists_link, self.trakt_user)
			except:
				userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
		except: pass
		self.list = []
		for i in range(len(userlists)): # Filter the user's own lists that were
			contains = False
			adapted = userlists[i]['url'].replace('/me/', '/%s/' % self.trakt_user)
			for j in range(len(self.list)):
				if adapted == self.list[j]['url'].replace('/me/', '/%s/' % self.trakt_user):
					contains = True
					break
			if not contains:
				self.list.append(userlists[i])
		for i in range(0, len(self.list)): self.list[i].update({'image': 'trakt.png', 'action': 'calendar'})
		if self.traktCredentials: # Trakt Watchlist
			self.list.insert(0, {'name': control.lang(32033), 'url': self.traktwatchlist_link, 'image': 'trakt.png', 'icon': 'DefaultVideoPlaylists.png', 'action': 'tvshows'})
		self.addDirectory(self.list, queue=True)
		return self.list

	def tmdb_list(self, tvshowtitle, imdb, tmdb, tvdb, meta, season):
		if not tmdb and (imdb or tvdb):
			try:
				result = cache.get(tmdb_indexer.TVshows().IdLookup, 96, imdb, tvdb)
				tmdb = str(result.get('id')) if result.get('id') else ''
			except:
				if control.setting('debug.level') != '1': return
				from resources.lib.modules import log_utils
				log_utils.log('tvshowtitle: (%s) missing tmdb_id' % tvshowtitle, __name__, log_utils.LOGDEBUG) # log TMDb does not have show
		seasonEpisodes = cache.get(tmdb_indexer.TVshows().get_seasonEpisodes_meta, 96, tmdb, season)
		if not seasonEpisodes: return
		if not isinstance(meta, dict): showSeasons = jsloads(meta)
		else: showSeasons = meta
		list = []
		unaired_count = 0
		for item in seasonEpisodes['episodes']:
			try:
				values = {}
				values.update(seasonEpisodes)
				values.update(item)
				values['tvshowtitle'] = tvshowtitle
				values['year'] = showSeasons.get('year')
				values['trailer'] = showSeasons.get('trailer')
				values['imdb'] = imdb
				values['tvdb'] = tvdb
				values['aliases'] = showSeasons.get('aliases', [])
				values['total_seasons'] = showSeasons.get('total_seasons')
				values['counts'] = showSeasons.get('counts')
				values['studio'] = showSeasons.get('studio')
				values['genre'] = showSeasons.get('genre')
				try: values['duration'] = int(showSeasons.get('duration')) # showSeasons already converted to seconds
				except: values['duration'] = ''
				values['mpaa'] = showSeasons.get('mpaa')
				values['status'] = showSeasons.get('status')
				values['unaired'] = ''
				try:
					if values['status'].lower() == 'ended': pass
					elif not values['premiered']:
						values['unaired'] = 'true'
						unaired_count += 1
						if not self.showunaired: continue
						pass
					elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
						values['unaired'] = 'true'
						unaired_count += 1
						if not self.showunaired: continue
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
				values['poster'] = item.get('poster') or showSeasons.get('poster')
				values['season_poster'] = item.get('season_poster') or showSeasons.get('season_poster')
				values['fanart'] = showSeasons.get('fanart')
				values['icon'] = showSeasons.get('icon')
				values['banner'] = showSeasons.get('banner')
				values['clearlogo'] = showSeasons.get('clearlogo')
				values['clearart'] = showSeasons.get('clearart')
				values['landscape'] = showSeasons.get('landscape')
				values['extended'] = True # used to bypass calling "super_info()", super_info() no longer used as of 4-12-21 so this could be removed.
				for k in ('episodes',): values.pop(k, None) # pop() keys from seasonEpisodes that are not needed anymore
				list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		for i in range(0, len(list)): list[i].update({'season_isAiring': 'true' if unaired_count >0 else 'false'}) # update for if "season_isAiring", needed for season pack scraping
		return list

	def trakt_user_list(self, url, user):
		try:
			result = trakt.getTrakt(url)
			items = jsloads(result)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
		for item in items:
			try:
				try: name = item['list']['name']
				except: name = item['name']
				name = client.replaceHTMLCodes(name)
				try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
				except: url = ('me', item['ids']['slug'])
				url = self.traktlist_link % url
				self.list.append({'name': name, 'url': url})
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		self.list = sorted(self.list, key=lambda k: re.sub(r'(^the |^a |^an )', '', k['name'].lower()))
		return self.list

	def trakt_progress_list(self, url, user, lang, direct=False, upcoming=False):
		try:
			url += '?extended=full'
			result = trakt.getTrakt(url)
			result = jsloads(result)
		except: return
		items = []
		progress_showunaired = control.setting('trakt.progress.showunaired') == 'true'
		for item in result:
			try:
				values = {} ; num_1 = 0
				if not upcoming and item['show']['status'].lower() == 'ended': # only chk ended cases for all watched otherwise airing today cases get dropped.
					for i in range(0, len(item['seasons'])):
						if item['seasons'][i]['number'] > 0: num_1 += len(item['seasons'][i]['episodes'])
					num_2 = int(item['show']['aired_episodes']) # trakt slow to update "aired_episodes" count on day item airs
					if num_1 >= num_2: continue
				season_sort = sorted(item['seasons'][:], key=lambda k: k['number'], reverse=False) # trakt sometimes places season0 at end and episodes out of order. So we sort it to be sure.
				values['snum'] = season_sort[-1]['number']
				episode = [x for x in season_sort[-1]['episodes'] if 'number' in x]
				episode = sorted(episode, key=lambda x: x['number'])
				values['enum'] = episode[-1]['number']
				values['added'] = item.get('show').get('updated_at')
				try: values['lastplayed'] = item.get('last_watched_at')
				except: values['lastplayed'] = ''
				values['tvshowtitle'] = item['show']['title']
				if not values['tvshowtitle']: continue
				ids = item.get('show', {}).get('ids', {})
				values['imdb'] = str(ids.get('imdb', '')) if ids.get('imdb') else ''
				values['tmdb'] = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
				values['tvdb'] = str(ids.get('tvdb', '')) if ids.get('tvdb') else ''
				try: values['trailer'] = control.trailer % item['show']['trailer'].split('v=')[1]
				except: values['trailer'] = ''
				try:
					airs = item['show']['airs']
					values['airday'] = airs.get('day', '')
					values['airtime'] = airs.get('time', '')
					values['airzone'] = airs.get('timezone', '')
				except: pass
				items.append(values)
			except: pass
		try:
			result = cache.get(trakt.getTrakt, 0, self.hiddenprogress_link) # if this gets cached and user hides an item it's not instantly removed.
			result = jsloads(result)
			result = [str(i['show']['ids']['tvdb']) for i in result]
			items = [i for i in items if i['tvdb'] not in result] # removes hidden progress items
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			pass

		def items_list(i):
			values = i
			imdb, tmdb, tvdb = i.get('imdb'), i.get('tmdb'), i.get('tvdb')
			if not tmdb and (imdb or tvdb):
				try:
					result = cache.get(tmdb_indexer.TVshows().IdLookup, 96, imdb, tvdb)
					values['tmdb'] = str(result.get('id', '')) if result.get('id') else ''
				except:
					from resources.lib.modules import log_utils
					log_utils.log('tvshowtitle: (%s) missing tmdb_id' % i['tvshowtitle'], __name__, log_utils.LOGDEBUG) # log TMDb does not have show
					return
			try:
				showSeasons = cache.get(tmdb_indexer.TVshows().get_showSeasons_meta, 96, tmdb)
				if not showSeasons: return
				key = i['snum'] - 1 if showSeasons['seasons'][0]['season_number'] != 0 else i['snum']
				try: next_episode_num = i['enum'] + 1 if showSeasons['seasons'][key]['episode_count'] > i['enum'] else 1
				except: return
				next_season_num = i['snum'] if next_episode_num == i['enum'] + 1 else i['snum'] + 1
				if next_season_num > showSeasons['total_seasons']: return
				if not self.showspecials and next_season_num == 0: return
				seasonEpisodes = cache.get(tmdb_indexer.TVshows().get_seasonEpisodes_meta, 96, tmdb, next_season_num)
				if not seasonEpisodes: return
				try: episode_meta = [x for x in seasonEpisodes.get('episodes') if x.get('episode') == next_episode_num][0] # to pull just the episode meta we need
				except: return
				if not episode_meta['plot']: episode_meta['plot'] = showSeasons['plot'] # some plots missing for eps so use season level plot
				values.update(showSeasons)
				values.update(seasonEpisodes)
				values.update(episode_meta)
				for k in ('seasons', 'episodes', 'snum', 'enum'): values.pop(k, None) # pop() keys from showSeasons and seasonEpisodes that are not needed anymore
				values['unaired'] = ''
				if upcoming:
					values['traktUpcomingProgress'] = True
					try:
						if values['status'].lower() == 'ended': return
						elif not values['premiered']: values['unaired'] = 'true'
						elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) > int(re.sub(r'[^0-9]', '', str(self.today_date))): values['unaired'] = 'true'
						elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) == int(re.sub(r'[^0-9]', '', str(self.today_date))):
							time_now = (self.date_time).strftime('%X')
							if int(re.sub(r'[^0-9]', '', str(values['airtime']))) > int(re.sub(r'[^0-9]', '', str(time_now))[:4]): values['unaired'] = 'true'
							else: return
						else: return
					except:
						from resources.lib.modules import log_utils
						log_utils.error()
				else:
					try:
						if values['status'].lower() == 'ended': pass
						elif not values['premiered']:
							values['unaired'] = 'true'
							if not progress_showunaired: return
						elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
							values['unaired'] = 'true'
							if not progress_showunaired: return
						elif int(re.sub(r'[^0-9]', '', str(values['premiered']))) == int(re.sub(r'[^0-9]', '', str(self.today_date))):
							time_now = (self.date_time).strftime('%X')
							if int(re.sub(r'[^0-9]', '', str(values['airtime']))) > int(re.sub(r'[^0-9]', '', str(time_now))[:4]):
								values['unaired'] = 'true'
								if not progress_showunaired: return
					except:
						from resources.lib.modules import log_utils
						log_utils.error()
				if not direct: values['action'] = 'episodes' # for direct progress scraping
				values['traktProgress'] = True # for direct progress scraping and multi episode watch counts indicators
				values['extended'] = True # used to bypass calling "super_info()", super_info() no longer used as of 4-12-21 so this could be removed.
				if not self.disable_fanarttv:
					extended_art = cache.get(fanarttv.get_tvshow_art, 168, tvdb)
					if extended_art: values.update(extended_art)
				self.list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		threads = []
		for i in items:
			threads.append(workers.Thread(items_list, i))
		[i.start() for i in threads]
		[i.join() for i in threads]
		return self.list

	def trakt_list(self, url, user, count=False):
		try:
			for i in re.findall(r'date\[(\d+)\]', url):
				url = url.replace('date[%s]' % i, (self.date_time - timedelta(days=int(i))).strftime('%Y-%m-%d'))
			q = dict(parse_qsl(urlsplit(url).query))
			q.update({'extended': 'full'})
			q = (urlencode(q)).replace('%2C', ',')
			u = url.replace('?' + urlparse(url).query, '') + '?' + q
			itemlist = []
			items = trakt.getTraktAsJson(u)
		except: return
		try:
			q = dict(parse_qsl(urlsplit(url).query))
			if int(q['limit']) != len(items): raise Exception()
			q.update({'page': str(int(q['page']) + 1)})
			q = (urlencode(q)).replace('%2C', ',')
			next = url.replace('?' + urlparse(url).query, '') + '?' + q
		except: next = ''

		for item in items:
			try:
				if 'show' not in item or 'episode' not in item: continue
				title = item['episode']['title']
				if not title: continue
				try:
					season = item['episode']['season']
					episode = item['episode']['number']
				except: continue
				if not self.showspecials and season == 0: continue
				tvshowtitle = item.get('show').get('title')
				if not tvshowtitle: continue
				year = str(item.get('show').get('year'))
				try: progress = max(0, min(1, item['progress'] / 100.0))
				except: progress = None
				ids = item.get('show', {}).get('ids', {})
				imdb = str(ids.get('imdb', '')) if ids.get('imdb') else ''
				tmdb = str(ids.get('tmdb', '')) if ids.get('tmdb') else ''
				tvdb = str(ids.get('tvdb', '')) if ids.get('tvdb') else ''
				episodeIDS = item.get('episode').get('ids', {}) # not used anymore
				premiered = item.get('episode').get('first_aired') #leave timestamp for better sort of the day
				added = item['episode']['updated_at'] or item.get('show').get('updated_at', '')
				try: lastplayed = item.get('watched_at', '')
				except: lastplayed = ''
				paused_at = item.get('paused_at', '')
				studio = item.get('show').get('network')
				genre = []
				for i in item['show']['genres']: genre.append(i.title())
				if genre == []: genre = 'NA'
				try: duration = int(item['episode']['runtime']) * 60
				except:
					try:duration = int(item.get('show').get('runtime')) * 60
					except: duration = ''
				rating = str(item.get('episode').get('rating'))
				votes = str(format(int(item.get('episode').get('votes')),',d'))
				mpaa = item.get('show').get('certification')
				plot = item['episode']['overview'] or item['show']['overview']
				if self.lang != 'en':
					try:
						trans_item = trakt.getTVShowTranslation(imdb, lang=self.lang, season=season, episode=episode,  full=True)
						title = trans_item.get('title') or title
						plot = trans_item.get('overview') or plot
						tvshowtitle = trakt.getTVShowTranslation(imdb, lang=self.lang) or tvshowtitle
					except:
						from resources.lib.modules import log_utils
						log_utils.error()
				try: trailer = control.trailer % item['show']['trailer'].split('v=')[1]
				except: trailer = ''
				values = {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered,
							'added': added, 'lastplayed': lastplayed, 'progress': progress, 'paused_at': paused_at, 'status': 'Continuing',
							'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot,
							'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'trailer': trailer, 'episodeIDS': episodeIDS, 'next': next}
				try:
					airs = item['show']['airs']
					values['airday'] = airs.get('day', '')
					values['airtime'] = airs.get('time', '')
					values['airzone'] = airs.get('timezone', '')
				except: pass
				itemlist.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return itemlist

	def trakt_episodes_list(self, url, user, lang, direct=True):
		self.list = []
		items = self.trakt_list(url, user)
		def items_list(i):
			values = i
			tmdb, tvdb = i['tmdb'], i['tvdb']
			try:
				seasonEpisodes = cache.get(tmdb_indexer.TVshows().get_seasonEpisodes_meta, 96, tmdb, i['season'])
				if not seasonEpisodes: return
				try: episode_meta = [x for x in seasonEpisodes.get('episodes') if x.get('episode') == i['episode']][0] # to pull just the episode meta we need
				except: return
				# if not episode_meta['plot']: episode_meta['plot'] = values['plot'] # some plots missing for eps so use season level plot
				values.update(seasonEpisodes)
				values.update(episode_meta)
				for k in ('episodes',): values.pop(k, None) # pop() keys from seasonEpisodes that are not needed anymore
				try:
					art = cache.get(tmdb_indexer.TVshows().get_art, 96, tmdb)
					values.update(art)
				except: pass
				if not self.disable_fanarttv:
					extended_art = cache.get(fanarttv.get_tvshow_art, 168, tvdb)
					if extended_art: values.update(extended_art)
				values['extended'] = True # used to bypass calling "super_info()", super_info() no longer used as of 4-12-21 so this could be removed.
				if not direct: values['action'] = 'episodes'
				self.list.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		threads = []
		for i in items:
			threads.append(workers.Thread(items_list, i))
		[i.start() for i in threads]
		[i.join() for i in threads]
		return self.list

	def tvmaze_list(self, url, limit, count=False):
		try:
			result = client.request(url, error=True)
			result = jsloads(result)
		except: return
		items = []
		for item in result:
			values = {}
			try:
				if not item['show']['language']: continue
				if 'english' not in item['show']['language'].lower(): continue
				if limit and 'scripted' not in item['show']['type'].lower(): continue
				values['title'] = item.get('name')
				values['season'] = item['season']
				if not values['season']: continue
				if not self.showspecials and values['season'] == 0: continue
				values['episode'] = item['number']
				if values['episode'] is None: continue
				values['premiered'] = item.get('airdate', '')
				try: values['year'] = str(item.get('show', {}).get('premiered', ''))[:4] # shows year
				except: values['year'] = ''
				values['tvshowtitle'] = item.get('show', {}).get('name')
				ids = item.get('show', {}).get('externals', {})
				imdb = str(ids.get('imdb', '')) if ids.get('imdb') else ''
				tmdb = '' # TVMaze does not have tmdb in their api
				tvdb = str(ids.get('thetvdb', '')) if ids.get('thetvdb') else ''
				try: values['poster'] = item['show']['image']['original']
				except: values['poster'] = ''
				try: values['thumb'] = item['image']['original']
				except: values['thumb'] = ''
				if not values['thumb']: values['thumb'] = values['poster']
				studio = item.get('show').get('webChannel') or item.get('show').get('network')
				values['studio'] = studio.get('name') or ''
				values['genre'] = []
				for i in item['show']['genres']: values['genre'].append(i.title())
				try: values['duration'] = int(item.get('show', {}).get('runtime', '')) * 60
				except: values['duration'] = ''
				values['rating'] = str(item.get('show', {}).get('rating', {}).get('average', ''))
				try: values['status'] = str(item.get('show', {}).get('status', ''))
				except: values['status'] = 'Continuing'
				try:
					plot = item.get('show', {}).get('summary', '')
					values['plot'] = re.sub(r'<.+?>|</.+?>|\n', '', plot)
				except: values['plot'] = ''
				try: values['airday'] = item['show']['schedule']['days'][0]
				except: values['airday'] = ''
				values['airtime'] = item['airtime'] or ''
				try: values['airzone'] = item['show']['network']['country']['timezone']
				except: values['airzone'] = ''
				values['extended'] = True
				values['ForceAirEnabled'] = True
				if control.setting('tvshows.calendar.extended') == 'true':
					if imdb:
						trakt_ids = trakt.IdLookup('imdb', imdb, 'show')
						if trakt_ids:
							if not tvdb: tvdb = str(trakt_ids.get('tvdb', '')) if trakt_ids.get('tvdb') else ''
							tmdb = str(trakt_ids.get('tmdb', '')) if trakt_ids.get('tmdb') else ''
					elif not imdb and tvdb:
						trakt_ids = trakt.IdLookup('tvdb', tvdb, 'show')
						if trakt_ids:
							imdb = str(trakt_ids.get('imdb', '')) if trakt_ids.get('imdb') else ''
							tmdb = str(trakt_ids.get('tmdb', '')) if trakt_ids.get('tmdb') else ''
					if not values['poster'] or not values['thumb']:
						try:
							art = cache.get(tmdb_indexer.TVshows().get_art, 96, tmdb)
							if not values['poster']: values['poster'] = art['poster3'] or ''
							if not values['thumb']: values['thumb'] = art['fanart3'] or ''
						except: pass
					if not values['thumb']: values['thumb'] = values['poster']
					values['fanart'] = values['thumb']
					values['season_poster'] = values['poster']
					if not self.disable_fanarttv:
						extended_art = cache.get(fanarttv.get_tvshow_art, 168, tvdb)
						if extended_art: values.update(extended_art)
				values['imdb'] = imdb
				values['tmdb'] = tmdb
				values['tvdb'] = tvdb
				items.append(values)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		return items

	def episodeDirectory(self, items, unfinished=False, next=True):
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32326, message=33049)
		from resources.lib.modules.player import Bookmarks
		sysaddon, syshandle = argv[0], int(argv[1])
		is_widget = 'plugin' not in control.infoLabel('Container.PluginName')
		if not is_widget: control.playlist.clear()
		settingFanart = control.setting('fanart') == 'true'
		addonPoster, addonFanart, addonBanner = control.addonPoster(), control.addonFanart(), control.addonBanner()
		try: traktProgress = False if 'traktProgress' not in items[0] else True
		except: traktProgress = False
		if traktProgress and control.setting('tvshows.direct') == 'false': progressMenu = control.lang(32015)
		else: progressMenu = control.lang(32016)
		if traktProgress: isMultiList = True
		else:
			try: multi = [i['tvshowtitle'] for i in items]
			except: multi = []
			isMultiList = True if len([x for y, x in enumerate(multi) if x not in multi[:y]]) > 1 else False
			try:
				if '/users/me/history/' in items[0]['next']: isMultiList = True
			except: pass
		upcoming_prependDate = control.setting('trakt.UpcomingProgress.prependDate') == 'true'
		try: sysaction = items[0]['action']
		except: sysaction = ''
		unwatchedEnabled = control.setting('tvshows.unwatched.enabled') == 'true'
		multi_unwatchedEnabled = control.setting('multi.unwatched.enabled') == 'true'
		try: airEnabled = control.setting('tvshows.air.enabled') if 'ForceAirEnabled' not in items[0] else 'true'
		except: airEnabled = 'false'
		play_mode = control.setting('play.mode')
		enable_playnext = control.setting('enable.playnext') == 'true'
		indicators = getTVShowIndicators(refresh=True)
		isFolder = False if sysaction != 'episodes' else True
		if airEnabled == 'true':
			airZone, airLocation = control.setting('tvshows.air.zone'), control.setting('tvshows.air.location')
			airFormat, airFormatDay = control.setting('tvshows.air.format'), control.setting('tvshows.air.day')
			airFormatTime, airBold = control.setting('tvshows.air.time'), control.setting('tvshows.air.bold')
			airLabel = control.lang(35032)
		if play_mode == '1' or enable_playnext: playbackMenu = control.lang(32063)
		else: playbackMenu = control.lang(32064)
		if trakt.getTraktIndicatorsInfo():
			watchedMenu, unwatchedMenu = control.lang(32068), control.lang(32069)
		else:
			watchedMenu, unwatchedMenu = control.lang(32066), control.lang(32067)
		traktManagerMenu, playlistManagerMenu, queueMenu = control.lang(32070), control.lang(35522), control.lang(32065)
		tvshowBrowserMenu, addToLibrary = control.lang(32071), control.lang(32551)
		clearSourcesMenu = control.lang(32611)
		for i in items:
			try:
				tvshowtitle, title, imdb, tmdb, tvdb = i.get('tvshowtitle'), i.get('title'), i.get('imdb', ''), i.get('tmdb', ''), i.get('tvdb', '')
				year, season, episode, premiered = i.get('year', ''), i.get('season'), i.get('episode'), i.get('premiered', '')
				trailer, runtime = i.get('trailer', ''), i.get('duration')
				if 'label' not in i: i['label'] = title
				if (not i['label'] or i['label'] == '0'): label = '%sx%02d . %s %s' % (season, int(episode), 'Episode', episode)
				else: label = '%sx%02d . %s' % (season, int(episode), i['label'])
				if isMultiList: label = '%s - %s' % (tvshowtitle, label)
				try: labelProgress = label + '[COLOR %s]  [%s][/COLOR]' % (self.highlight_color, str(round(float(i['progress'] * 100), 1)) + '%')
				except: labelProgress = label
				try:
					if i['unaired'] == 'true': labelProgress = '[COLOR %s][I]%s[/I][/COLOR]' % (self.unairedcolor, labelProgress)
				except: pass
				if i.get('traktHistory') is True:
					try:
						air_datetime = tools.Time.convert(stringTime=i.get('lastplayed', ''), zoneFrom='utc', zoneTo='local', formatInput='%Y-%m-%dT%H:%M:%S.000Z', formatOutput='%b %d %Y %I:%M %p')
						if air_datetime[12] == '0': air_datetime = air_datetime[:12] + '' + air_datetime[13:]
						labelProgress = labelProgress + '[COLOR %s]  [%s][/COLOR]' % (self.highlight_color, air_datetime)
					except: pass
				if upcoming_prependDate and i.get('traktUpcomingProgress') is True:
					try:
						if premiered and i.get('airtime'): combined='%sT%s' % (premiered, i.get('airtime', ''))
						else: raise Exception()
						air_datetime = tools.Time.convert(stringTime=combined, zoneFrom=i.get('airzone', ''), zoneTo='local', formatInput='%Y-%m-%dT%H:%M', formatOutput='%b %d %I:%M %p')
						if air_datetime[7] == '0': air_datetime = air_datetime[:7] + '' + air_datetime[8:]
						labelProgress = labelProgress + '[COLOR %s]  [%s][/COLOR]' % (self.highlight_color, air_datetime)
					except: pass
				systitle, systvshowtitle, syspremiered = quote_plus(title), quote_plus(tvshowtitle), quote_plus(premiered)
				meta = dict((k, v) for k, v in iter(i.items()) if v is not None and v != '')
				meta.update({'code': imdb, 'imdbnumber': imdb, 'mediatype': 'episode', 'tag': [imdb, tmdb]}) # "tag" and "tagline" for movies only, but works in my skin mod so leave
				try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
				except: pass
				try: meta.update({'title': i['label']})
				except: pass
				if airEnabled == 'true':
					air = [] ; airday = None ; airtime = None
					if 'airday' in meta and not meta['airday'] is None and meta['airday'] != '':
						airday = meta['airday']
					if 'airtime' in meta and not meta['airtime'] is None and meta['airtime'] != '':
						airtime = meta['airtime']
						if 'airzone' in meta and not meta['airzone'] is None and meta['airzone'] != '':
							if airZone == '1': zoneTo = meta['airzone']
							elif airZone == '2': zoneTo = 'utc'
							else: zoneTo = 'local'
							if airFormatTime == '1': formatOutput = '%I:%M'
							elif airFormatTime == '2': formatOutput = '%I:%M %p'
							else: formatOutput = '%H:%M'
							abbreviate = airFormatDay == '1'
							airtime = tools.Time.convert(stringTime=airtime, stringDay=airday, zoneFrom=meta['airzone'], zoneTo=zoneTo, abbreviate=abbreviate, formatOutput=formatOutput)
							if airday: airday, airtime = airtime[1], airtime[0]
					if airday: air.append(airday)
					if airtime: air.append(airtime)
					if len(air) > 0:
						if airFormat == '0': air = airtime
						elif airFormat == '1': air = airday
						elif airFormat == '2': air = air = ' '.join(air)
						if airLocation == '0' or airLocation == '1': air = '[COLOR skyblue][%s][/COLOR]' % air
						if airBold == 'true': air = '[B]%s[/B]' % str(air)
						if airLocation == '0': labelProgress = '%s %s' % (air, labelProgress)
						elif airLocation == '1': labelProgress = '%s %s' % (labelProgress, air)
						elif airLocation == '2': meta['plot'] = '%s%s\r\n%s' % (airLabel, air, meta['plot'])
						elif airLocation == '3': meta['plot'] = '%s\r\n%s%s' % (meta['plot'], airLabel, air)
				poster = meta.get('poster3') or meta.get('poster2') or meta.get('poster') or addonPoster
				season_poster = meta.get('season_poster') or poster
				landscape = meta.get('landscape')
				fanart = ''
				if settingFanart: fanart = meta.get('fanart3') or meta.get('fanart2') or meta.get('fanart') or landscape or addonFanart
				thumb = meta.get('thumb') or landscape or fanart or season_poster
				icon = meta.get('icon') or season_poster or poster
				banner = meta.get('banner3') or meta.get('banner2') or meta.get('banner') or addonBanner
				art = {}
				art.update({'poster': season_poster, 'tvshow.poster': poster, 'season.poster': season_poster, 'fanart': fanart, 'icon': icon, 'thumb': thumb, 'banner': banner,
						'clearlogo': meta.get('clearlogo', ''), 'tvshow.clearlogo': meta.get('clearlogo', ''), 'clearart': meta.get('clearart', ''), 'tvshow.clearart': meta.get('clearart', ''), 'landscape': thumb})
				for k in ('poster2', 'poster3', 'fanart2', 'fanart3', 'banner2', 'banner3', 'trailer'): meta.pop(k, None)
				meta.update({'poster': poster, 'fanart': fanart, 'banner': banner, 'thumb': thumb, 'icon': icon})
####-Context Menu and Overlays-####
				cm = []
				try:
					overlay = int(getEpisodeOverlay(indicators, imdb, tvdb, season, episode))
					watched = (overlay == 5)
					if self.traktCredentials:
						cm.append((traktManagerMenu, 'RunPlugin(%s?action=tools_traktManager&name=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&watched=%s)' % (sysaddon, systvshowtitle, imdb, tvdb, season, episode, watched)))
					if watched:
						meta.update({'playcount': 1, 'overlay': 5})
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=playcount_Episode&name=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&query=4)' % (sysaddon, systvshowtitle, imdb, tvdb, season, episode)))
					else:
						meta.update({'playcount': 0, 'overlay': 4})
						cm.append((watchedMenu, 'RunPlugin(%s?action=playcount_Episode&name=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&query=5)' % (sysaddon, systvshowtitle, imdb, tvdb, season, episode)))
				except: pass
				sysmeta, sysart, syslabelProgress = quote_plus(jsdumps(meta)), quote_plus(jsdumps(art)), quote_plus(labelProgress)
				url = '%s?action=play_Item&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (
										sysaddon, systitle, year, imdb, tmdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)
				sysurl = quote_plus(url)
				Folderurl = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&meta=%s&season=%s&episode=%s&art=%s' % (sysaddon, systvshowtitle, year, imdb, tmdb, tvdb, sysmeta, season, episode, sysart)
				if isFolder:
					if traktProgress:
						cm.append((progressMenu, 'PlayMedia(%s)' % url))
					url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&meta=%s&season=%s&episode=%s&art=%s' % (sysaddon, systvshowtitle, year, imdb, tmdb, tvdb, sysmeta, season, episode, sysart)
				cm.append((playlistManagerMenu, 'RunPlugin(%s?action=playlist_Manager&name=%s&url=%s&meta=%s&art=%s)' % (sysaddon, syslabelProgress, sysurl, sysmeta, sysart)))
				cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem&name=%s)' % (sysaddon, syslabelProgress)))
				if isMultiList:
					cm.append((tvshowBrowserMenu, 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&art=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tmdb, tvdb, sysart)))
				if not isFolder:
					if traktProgress: cm.append((progressMenu, 'Container.Update(%s)' % Folderurl))
					cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
					cm.append(('Rescrape Item', 'PlayMedia(%s?action=play_Item&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&rescrape=true)' % (
										sysaddon, systitle, year, imdb, tmdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)))
				cm.append((addToLibrary, 'RunPlugin(%s?action=library_tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s)' % (sysaddon, systvshowtitle, year, imdb, tmdb, tvdb)))
				cm.append((clearSourcesMenu, 'RunPlugin(%s?action=cache_clearSources)' % sysaddon))
				# cm.append(('PlayAll', 'RunPlugin(%s?action=play_All)' % sysaddon))
				cm.append(('[COLOR white]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
####################################
				if trailer: meta.update({'trailer': trailer})
				else: meta.update({'trailer': '%s?action=play_Trailer&type=%s&name=%s&year=%s&imdb=%s' % (sysaddon, 'show', syslabelProgress, year, imdb)})
				item = control.item(label=labelProgress, offscreen=True)
				if 'castandart' in i: item.setCast(i['castandart'])
				item.setArt(art)
				if isMultiList and (unwatchedEnabled and multi_unwatchedEnabled):
					if 'ForceAirEnabled' not in i:
						try:
							count = getShowCount(indicators, imdb, tvdb) # this is threaded without .join() so not all results are immediately seen
							if count:
								item.setProperties({'WatchedEpisodes': str(count['watched']), 'UnWatchedEpisodes': str(count['unwatched'])})
								item.setProperties({'TotalSeasons': str(meta.get('total_seasons', '')), 'TotalEpisodes': str(count['total'])})
							else:
								item.setProperties({'WatchedEpisodes': '0', 'UnWatchedEpisodes': str(meta.get('total_aired_episodes', ''))}) # temp use TMDb's "total_aired_episodes" for threads not finished....next load counts will update with trakt data
								item.setProperties({'TotalSeasons': str(meta.get('total_seasons', '')), 'TotalEpisodes': str(meta.get('total_aired_episodes', ''))})
						except: pass

				item.setProperty('IsPlayable', 'true')
				item.setProperty('tvshow.tmdb_id', tmdb)
				if is_widget: item.setProperty('isDG_widget', 'true')
				blabel = tvshowtitle + ' S%02dE%02d' % (int(season), int(episode))
				resumetime = Bookmarks().get(name=blabel, imdb=imdb, tmdb=tmdb, tvdb=tvdb, season=season, episode=episode, year=str(year), runtime=runtime, ck=True)
				# item.setProperty('TotalTime', str(meta.get('duration'))) # Adding this property causes the Kodi bookmark CM items to be added
				item.setProperty('ResumeTime', str(resumetime))
				try:
					watched_percent = round(float(resumetime) / float(runtime) * 100, 1) # resumetime and runtime are both in minutes
					item.setProperty('percentplayed', str(watched_percent))
				except: pass
				try: # Year is the shows year, not the seasons year. Extract year from premier date for infoLabels to have "season_year."
					season_year = re.findall(r'(\d{4})', i.get('premiered', ''))[0]
					meta.update({'year': season_year})
				except: pass
				item.setUniqueIDs({'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb})
				if upcoming_prependDate and i.get('traktUpcomingProgress') is True:
					try:
						if premiered and meta.get('airtime'): combined='%sT%s' % (premiered, meta.get('airtime', ''))
						else: raise Exception()
						air_datetime = tools.Time.convert(stringTime=combined, zoneFrom=meta.get('airzone', ''), zoneTo='local', formatInput='%Y-%m-%dT%H:%M', formatOutput='%b %d %I:%M %p')
						if air_datetime[7] == '0': air_datetime = air_datetime[:7] + '' + air_datetime[8:]
						new_title = '[COLOR %s][%s]  [/COLOR]' % (self.highlight_color, air_datetime) + title
						meta.update({'title': new_title})
					except: pass
				item.setInfo(type='video', infoLabels=control.metadataClean(meta))
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
				# if not traktProgress or not isMultiList:
					# if playlistcreate: control.playlist.add(url=url, listitem=item)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		if next:
			try:
				if not items: raise Exception()
				url = items[0]['next']
				if not url: raise Exception()
				nextMenu = control.lang(32053)
				url_params = dict(parse_qsl(url))
				if 'imdb.com' in url:
					start = int(url_params.get('start'))
					page = '  [I](%s)[/I]' % str(((start - 1) / int(self.count)) + 1)
				else:
					page = url_params.get('page')
					page = '  [I](%s)[/I]' % page
				nextMenu = '[COLOR skyblue]' + nextMenu + page + '[/COLOR]'
				if '/users/me/history/' in url: url = '%s?action=calendar&url=%s' % (sysaddon, quote_plus(url))
				item = control.item(label=nextMenu, offscreen=True)
				icon = control.addonNext()
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
				item.setProperty ('SpecialSort', 'bottom')
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except: pass
		if isMultiList and (unwatchedEnabled and multi_unwatchedEnabled): # Show multi episodes as show, in order to display unwatched count if enabled.
			control.content(syshandle, 'tvshows')
			control.directory(syshandle, cacheToDisc=True)
			views.setView('tvshows', {'skin.estuary': 55, 'skin.confluence': 500})
		else:
			control.content(syshandle, 'episodes')
			control.directory(syshandle, cacheToDisc=True)
			views.setView('episodes', {'skin.estuary': 55, 'skin.confluence': 504})

	def addDirectory(self, items, queue=False):
		if not items: # with reuselanguageinvoker on an empty directory must be loaded, do not use sys.exit()
			control.hide() ; control.notification(title=32326, message=33049)
		sysaddon, syshandle = argv[0], int(argv[1])
		addonThumb = control.addonThumb()
		artPath = control.artPath()
		queueMenu = control.lang(32065)
		for i in items:
			try:
				name = i['name']
				if i['image'].startswith('http'): thumb = i['image']
				elif artPath: thumb = control.joinPath(artPath, i['image'])
				else: thumb = addonThumb
				icon = i.get('icon', 0)
				if not icon: icon = 'DefaultFolder.png'
				url = '%s?action=%s' % (sysaddon, i['action'])
				try: url += '&url=%s' % quote_plus(i['url'])
				except: pass
				cm = []
				if queue: cm.append((queueMenu, 'RunPlugin(%s?action=playlist_QueueItem)' % sysaddon))
				cm.append(('[COLOR white]DG Settings[/COLOR]', 'RunPlugin(%s?action=tools_openSettings)' % sysaddon))
				item = control.item(label=name, offscreen=True)
				item.setProperty('IsPlayable', 'false')
				item.setArt({'icon': icon, 'poster': thumb, 'thumb': thumb, 'fanart': control.addonFanart(), 'banner': thumb})
				item.addContextMenuItems(cm)
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				from resources.lib.modules import log_utils
				log_utils.error()
		control.content(syshandle, 'addons')
		control.directory(syshandle, cacheToDisc=True)
