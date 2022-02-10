# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import re
import requests
from sys import argv, exit as sysexit
from threading import Thread
from urllib.parse import quote_plus
from resources.lib.database import cache
from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import string_tools
from resources.lib.modules.source_utils import supported_video_extensions

getLS = control.lang
getSetting = control.setting
FormatDateTime = "%Y-%m-%dT%H:%M:%S.%fZ"
rest_base_url = 'https://api.real-debrid.com/rest/1.0/'
oauth_base_url = 'https://api.real-debrid.com/oauth/v2/'
unrestrict_link_url = 'unrestrict/link'
device_code_url = 'device/code?%s'
credentials_url = 'device/credentials?%s'
downloads_delete_url = 'downloads/delete'
add_magnet_url = 'torrents/addMagnet'
torrents_info_url = 'torrents/info'
select_files_url = 'torrents/selectFiles'
torrents_delete_url = 'torrents/delete'
check_cache_url = 'torrents/instantAvailability'
torrents_active_url = "torrents/activeCount"
hosts_domains_url = 'hosts/domains'
# hosts_status_url = 'hosts/status'
hosts_regex_url = 'hosts/regex'
rd_icon = control.joinPath(control.artPath(), 'realdebrid.png')
addonFanart = control.addonFanart()


class RealDebrid:
	name = "Real-Debrid"
	sort_priority = getSetting('realdebrid.priority')
	def __init__(self):
		self.hosters = None
		self.hosts = None
		self.cache_check_results = {}
		self.token = getSetting('realdebrid.token')
		self.client_ID = getSetting('realdebrid.client_id')
		if self.client_ID == '': self.client_ID = 'X245A4XAIBGVM'
		self.secret = getSetting('realdebrid.secret')
		self.device_code = ''
		self.auth_timeout = 0
		self.auth_step = 0
		self.server_notifications = getSetting('realdebrid.server.notifications')
		self.store_to_cloud = getSetting('realdebrid.saveToCloud') == 'true'

	def _get(self, url, fail_check=False, token_ck=False):
		try:
			original_url = url
			url = rest_base_url + url
			if self.token == '':
				log_utils.log('No Real-Debrid Token Found')
				return None
			# if not fail_check: # with fail_check=True new token does not get added
			if '?' not in url:
				url += "?auth_token=%s" % self.token
			else:
				url += "&auth_token=%s" % self.token
			response = requests.get(url, timeout=45) # cache checkiing of show packs results in random timeout at 30
			if 'Temporarily Down For Maintenance' in response.text:
				if self.server_notifications: control.notification(message='Real-Debrid Temporarily Down For Maintenance', icon=rd_icon)
				log_utils.log('Real-Debrid Temporarily Down For Maintenance', level=log_utils.LOGWARNING)
				return None
			else: response = response.json()
			if any(value in str(response) for value in ('bad_token', 'Bad Request')):
				if not fail_check:
					if self.refresh_token() and token_ck: return
					response = self._get(original_url, fail_check=True)
			return response
		except:
			log_utils.error()
		return None

	def _post(self, url, data):
		try:
			original_url = url
			url = rest_base_url + url
			if self.token == '':
				log_utils.log('No Real Debrid Token Found', level=log_utils.LOGWARNING)
				return None
			if '?' not in url:
				url += "?auth_token=%s" % self.token
			else:
				url += "&auth_token=%s" % self.token
			response = requests.post(url, data=data, timeout=15)
			if '[204]' in str(response): return None
			if 'Temporarily Down For Maintenance' in response.text:
				if self.server_notifications: control.notification(message='Real-Debrid Temporarily Down For Maintenance', icon=rd_icon)
				log_utils.log('Real-Debrid Temporarily Down For Maintenance', level=log_utils.LOGWARNING)
				return None
			else: response = response.json()
			if any(value in str(response) for value in ('bad_token', 'Bad Request')):
				self.refresh_token()
				response = self._post(original_url, data)
			elif 'error' in response:
				message = response.get('error')
				if message == 'action_already_done': return None
				if self.server_notifications: control.notification(message=message, icon=rd_icon)
				log_utils.log('Real-Debrid Error:  %s' % message, log_utils.LOGWARNING)
				return None
			return response
		except:
			log_utils.error()
		return None

	def auth_loop(self):
		control.sleep(self.auth_step*1000)
		url = 'client_id=%s&code=%s' % (self.client_ID, self.device_code)
		url = oauth_base_url + credentials_url % url
		response = requests.get(url)
		if 'error' in response.text:
			return control.okDialog(title='default', message=40019)
		else:
			try:
				response = response.json()
				control.progressDialog.close()
				self.client_ID = response['client_id']
				self.secret = response['client_secret']
			except:
				log_utils.error()
				control.okDialog(title='default', message=40019)
			return

	def auth(self):
		self.secret = ''
		self.client_ID = 'X245A4XAIBGVM'
		url = 'client_id=%s&new_credentials=yes' % self.client_ID
		url = oauth_base_url + device_code_url % url
		response = requests.get(url).json()
		line = '%s\n%s'
		progressDialog = control.progressDialog
		progressDialog.create(getLS(40055))
		progressDialog.update(-1, line % (getLS(32513) % 'https://real-debrid.com/device', getLS(32514) % response['user_code']))
		self.auth_timeout = int(response['expires_in'])
		self.auth_step = int(response['interval'])
		self.device_code = response['device_code']
		while self.secret == '':
			if progressDialog.iscanceled():
				progressDialog.close()
				break
			self.auth_loop()
		if self.secret: self.get_token()

	def account_info(self):
		return self._get('user')

	def account_info_to_dialog(self):
		from datetime import datetime
		import time
		try:
			userInfo = self.account_info()
			try: expires = datetime.strptime(userInfo['expiration'], FormatDateTime)
			except: expires = datetime(*(time.strptime(userInfo['expiration'], FormatDateTime)[0:6]))
			days_remaining = (expires - datetime.today()).days
			expires = expires.strftime("%A, %B %d, %Y")
			items = []
			items += [getLS(40035) % userInfo['email']]
			items += [getLS(40036) % userInfo['username']]
			items += [getLS(40037) % userInfo['type'].capitalize()]
			items += [getLS(40041) % expires]
			items += [getLS(40042) % days_remaining]
			items += [getLS(40038) % userInfo['points']]
			return control.selectDialog(items, 'Real-Debrid')
		except:
			log_utils.error()
		return

	def user_torrents(self):
		try:
			url = 'torrents'
			return self._get(url)
		except:
			log_utils.error()

	def user_torrents_to_listItem(self):
		try:
			sysaddon, syshandle = argv[0], int(argv[1])
			torrent_files = self.user_torrents()
			if not torrent_files: return
			# torrent_files = [i for i in torrent_files if i['status'] == 'downloaded']
			folder_str, deleteMenu = getLS(40046).upper(), getLS(40050)
			for count, item in enumerate(torrent_files, 1):
				try:
					cm = []
					isFolder = True if item['status'] == 'downloaded' else False
					status = '[COLOR %s]%s[/COLOR]' % (control.getHighlightColor(), item['status'].capitalize())
					folder_name = string_tools.strip_non_ascii_and_unprintable(item['filename'])
					label = '%02d | [B]%s[/B] - %s | [B]%s[/B] | [I]%s [/I]' % (count, status, str(item['progress']) + '%', folder_str, folder_name)
					url = '%s?action=rd_BrowseUserTorrents&id=%s' % (sysaddon, item['id']) if isFolder else None
					cm.append((deleteMenu % 'Torrent', 'RunPlugin(%s?action=rd_DeleteUserTorrent&id=%s&name=%s)' %
							(sysaddon, item['id'], quote_plus(folder_name))))
					item = control.item(label=label, offscreen=True)
					item.addContextMenuItems(cm)
					item.setArt({'icon': rd_icon, 'poster': rd_icon, 'thumb': rd_icon, 'fanart': addonFanart, 'banner': rd_icon})
					item.setInfo(type='video', infoLabels='')
					control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
				except:
					log_utils.error()
			control.content(syshandle, 'files')
			control.directory(syshandle, cacheToDisc=True)
		except:
			log_utils.error()

	def browse_user_torrents(self, folder_id):
		try:
			sysaddon, syshandle = argv[0], int(argv[1])
			torrent_files = self.torrent_info(folder_id)
		except: return
		extensions = supported_video_extensions()
		try:
			file_info = [i for i in torrent_files['files'] if i['path'].lower().endswith(tuple(extensions))]
			file_urls = torrent_files['links']
			for c, i in enumerate(file_info):
				try: i.update({'url_link': file_urls[c]})
				except: pass
			pack_info = sorted(file_info, key=lambda k: k['path'])
		except:
			if self.server_notifications: control.notification(message='Real-Debrid Error:  browse_user_torrents failed', icon=rd_icon)
			log_utils.log('Real-Debrid Error:  browse_user_torrents failed', __name__, log_utils.LOGWARNING)
			return
		file_str, downloadMenu, renameMenu, deleteMenu, clearFinishedMenu = \
				getLS(40047).upper(), getLS(40048), getLS(40049), getLS(40050), getLS(40051)
		for count, item in enumerate(pack_info, 1):
			try:
				cm = []
				try: url_link = item['url_link']
				except: continue
				if url_link.startswith('/'): url_link = 'http' + url_link
				name = item['path']
				if name.startswith('/'): name = name.split('/')[-1]
				size = float(int(item['bytes'])) / 1073741824
				label = '%02d | [B]%s[/B] | %.2f GB | [I]%s [/I]' % (count, file_str, size, name)
				url = '%s?action=play_URL&url=%s&caller=realdebrid&type=unrestrict' % (sysaddon, url_link)
				cm.append((downloadMenu, 'RunPlugin(%s?action=download&name=%s&image=%s&url=%s&caller=realdebrid&type=unrestrict)' %
							(sysaddon, quote_plus(name), quote_plus(rd_icon), url_link)))
				cm.append((deleteMenu % 'Torrent', 'RunPlugin(%s?action=rd_DeleteUserTorrent&id=%s&name=%s)' %
							(sysaddon, item['id'], quote_plus(name))))
				item = control.item(label=label, offscreen=True)
				item.addContextMenuItems(cm)
				item.setArt({'icon': rd_icon, 'poster': rd_icon, 'thumb': rd_icon, 'fanart': addonFanart, 'banner': rd_icon})
				item.setInfo(type='video', infoLabels='')
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
			except:
				log_utils.error()
		control.content(syshandle, 'files')
		control.directory(syshandle, cacheToDisc=True)

	def delete_user_torrent(self, media_id, name):
		try:
			if not control.yesnoDialog(getLS(40050) % '?\n' + name, '', ''): return
			ck_token = self._get('user', token_ck=True) # check token, and refresh if needed
			url = torrents_delete_url + "/%s&auth_token=%s" % (media_id, self.token)
			response = requests.delete(rest_base_url + url).text
			if not 'error' in response:
				log_utils.log('Real-Debrid: %s was removed from your active Torrents' % name, __name__, log_utils.LOGDEBUG)
				control.refresh()
				return
		except:
			log_utils.error('Real-Debrid Error: DELETE USER TORRENT %s : ' % name)
			raise

	def downloads(self, page):
		import math
		try:
			ck_token = self._get('user', token_ck=True) # check token, and refresh if needed
			url = 'downloads?page=%s&auth_token=%s' % (page, self.token)
			response = requests.get(rest_base_url + url)
			total_count = float(response.headers['X-Total-Count'])
			pages = int(math.ceil(total_count / 50.0))
			return response.json(), pages
		except:
			log_utils.error()

	def my_downloads_to_listItem(self, page):
		try:
			from datetime import datetime
			import time
			sysaddon, syshandle = argv[0], int(argv[1])
			my_downloads, pages = self.downloads(page)
		except: my_downloads = None
		if not my_downloads: return
		extensions = supported_video_extensions()
		my_downloads = [i for i in my_downloads if i['download'].lower().endswith(tuple(extensions))]
		downloadMenu, deleteMenu = getLS(40048), getLS(40050)
		for count, item in enumerate(my_downloads, 1):
			if page > 1: count += (page-1) * 50
			try: 
				cm = []
				try: datetime_object = datetime.strptime(item['generated'], FormatDateTime).date()
				except TypeError: datetime_object = datetime(*(time.strptime(item['generated'], FormatDateTime)[0:6])).date()
				name = string_tools.strip_non_ascii_and_unprintable(item['filename'])
				size = float(int(item['filesize'])) / 1073741824
				label = '%02d | %.2f GB | %s  | [I]%s [/I]' % (count, size, datetime_object, name)
				url_link = item['download']
				url = '%s?action=play_URL&url=%s' % (sysaddon, url_link)
				cm.append((downloadMenu, 'RunPlugin(%s?action=download&name=%s&image=%s&url=%s&caller=realdebrid)' %
								(sysaddon, quote_plus(name), quote_plus(rd_icon), url_link)))
				cm.append((deleteMenu % 'File', 'RunPlugin(%s?action=rd_DeleteDownload&id=%s&name=%s)' %
								(sysaddon, item['id'], name)))
				item = control.item(label=label, offscreen=True)
				item.addContextMenuItems(cm)
				item.setArt({'icon': rd_icon, 'poster': rd_icon, 'thumb': rd_icon, 'fanart': addonFanart, 'banner': rd_icon})
				item.setInfo(type='video', infoLabels='')
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
			except:
				log_utils.error()
		if page < pages:
			page += 1
			next = True
		else: next = False
		if next:
			try:
				nextMenu = getLS(32053)
				url = '%s?action=rd_MyDownloads&query=%s' % (sysaddon, page)
				page = '  [I](%s)[/I]' % page
				nextMenu = '[COLOR skyblue]' + nextMenu + page + '[/COLOR]'
				item = control.item(label=nextMenu, offscreen=True)
				icon = control.addonNext()
				item.setArt({'icon': rd_icon, 'poster': rd_icon, 'thumb': rd_icon, 'fanart': addonFanart, 'banner': rd_icon})
				control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
			except:
				log_utils.error()
		control.content(syshandle, 'files')
		control.directory(syshandle, cacheToDisc=True)

	def delete_download(self, media_id, name):
		try:
			if not control.yesnoDialog(getLS(40050) % '?\n' + name, '', ''): return
			ck_token = self._get('user', token_ck=True) # check token, and refresh if needed
			url = downloads_delete_url + "/%s&auth_token=%s" % (media_id, self.token)
			response = requests.delete(rest_base_url + url).text
			if response and not 'error' in response:
				if self.server_notifications: control.notification(message='Real-Debrid: %s was removed from your MyDownloads' % name, icon=rd_icon)
				log_utils.log('Real-Debrid: %s was removed from your MyDownloads' % name, __name__, log_utils.LOGDEBUG)
				control.refresh()
				return
		except:
			log_utils.error('Real-Debrid Error: DELETE DOWNLOAD %s : ' % name)

	def check_cache(self, hashList):
		# log_utils.log('len() of hashList sent=%s' % len(hashList))
		if isinstance(hashList, list):
			hashString = '/' + '/'.join(hashList)
		else:
			hashString = "/" + hashList
		response = self._get("torrents/instantAvailability" + hashString)
		# log_utils.log('len() of hashList received=%s' % len(response))
		return response

	def resolve_magnet(self, magnet_url, info_hash, season, episode, title):
		from resources.lib.modules.source_utils import seas_ep_filter, extras_filter
		from resources.lib.cloud_scrapers.cloud_utils import cloud_check_title
		try:
			torrent_id = None
			rd_url = None
			match = False
			reason = ''
			extensions = supported_video_extensions()
			extras_filtering_list = extras_filter()
			info_hash = info_hash.lower()
			if not season: compare_title = re.sub(r'[^A-Za-z0-9]+', '.', title.replace('\'', '').replace('&', 'and').replace('%', '.percent')).lower()
			torrent_files = self._get(check_cache_url + '/' + info_hash)
			if not info_hash in torrent_files: return None
			torrent_id = self.add_magnet(magnet_url) # add_magent() returns id
			torrent_files = torrent_files[info_hash]['rd']
			torrent_files = [item for item in torrent_files if self.video_only(item, extensions)]
			if not season:
				m2ts_check = self.m2ts_check(torrent_files)
				if m2ts_check: m2ts_key, torrent_files = self.m2ts_key_value(torrent_files) 
			for item in torrent_files:
				try:
					correct_file_check = False
					item_values = [i['filename'] for i in item.values()]
					if season:
						for value in item_values:
							if '.m2ts' in value:
								log_utils.log('Real-Debrid: Can not resolve .m2ts season disk episode', level=log_utils.LOGDEBUG)
								continue
							correct_file_check = seas_ep_filter(season, episode, value)
							if correct_file_check: break
						if not correct_file_check:
							reason = value + '  :no matching video filename'
							continue
					elif not m2ts_check:
						for value in item_values:
							filename = re.sub(r'[^A-Za-z0-9]+', '.', value.replace('\'', '').replace('&', 'and').replace('%', '.percent')).lower()
							filename_info = filename.replace(compare_title, '') 
							if any(x in filename_info for x in extras_filtering_list): continue
							aliases = self.get_aliases(title)
							correct_file_check = cloud_check_title(title, aliases, filename)
							if correct_file_check: break
						if not correct_file_check:
							reason = filename + '  :no matching video filename'
							continue
					torrent_keys = item.keys()
					if len(torrent_keys) == 0: continue
					torrent_keys = ','.join(torrent_keys)
					self.add_torrent_select(torrent_id, torrent_keys)
					torrent_info = self.torrent_info(torrent_id)
					if 'error' in torrent_info: continue
					selected_files = [(idx, i) for idx, i in enumerate([i for i in torrent_info['files'] if i['selected'] == 1])]
					if season:
						correct_files = []
						append = correct_files.append
						correct_file_check = False
						for value in selected_files:
							correct_file_check = seas_ep_filter(season, episode, value[1]['path'])
							if correct_file_check:
								append(value[1])
								break
						if len(correct_files) == 0: continue
						episode_title = re.sub(r'[^A-Za-z0-9]+', '.', title.replace("\'", '').replace('&', 'and').replace('%', '.percent')).lower()
						for i in correct_files:
							compare_link = seas_ep_filter(season, episode, i['path'], split=True)
							compare_link = re.sub(episode_title, '', compare_link)
							if any(x in compare_link for x in extras_filtering_list): continue
							else:
								match = True
								break
						if match:
							index = [i[0] for i in selected_files if i[1]['path'] == correct_files[0]['path']][0]
							break
					elif m2ts_check:
						match, index = True, [i[0] for i in selected_files if i[1]['id'] == m2ts_key][0]
					else:
						match = False
						for value in selected_files:
							filename = re.sub(r'[^A-Za-z0-9]+', '.', value[1]['path'].rsplit('/', 1)[1].replace('\'', '').replace('&', 'and').replace('%', '.percent')).lower()
							filename_info = filename.replace(compare_title, '') 
							if any(x in filename_info for x in extras_filtering_list): continue
							aliases = self.get_aliases(title)
							match = cloud_check_title(title, aliases, filename)
							if match:
								index = value[0]
								break
						if match: break
				except:
					log_utils.error()
			if match:
				rd_link = torrent_info['links'][index]
				file_url = self.unrestrict_link(rd_link)
				if file_url.endswith('rar'): file_url = None
				if not any(file_url.lower().endswith(x) for x in extensions): file_url = None
				if not self.store_to_cloud: self.delete_torrent(torrent_id)
				return file_url
			else:
				log_utils.log('Real-Debrid: FAILED TO RESOLVE MAGNET : "%s": %s' % (magnet_url, reason), __name__, log_utils.LOGWARNING)
			self.delete_torrent(torrent_id)
		except:
			log_utils.error('Real-Debrid: Error RESOLVE MAGNET %s : ' % magnet_url)
			if torrent_id: self.delete_torrent(torrent_id)
			return None

	def display_magnet_pack(self, magnet_url, info_hash):
		try:
			torrent_id = None
			video_only_items = []
			append = video_only_items.append
			list_file_items = []
			info_hash = info_hash.lower()
			extensions = supported_video_extensions()
			torrent_files = self._get(check_cache_url + '/' + info_hash)
			if not info_hash in torrent_files: return None
			torrent_id = self.add_magnet(magnet_url)
			if not torrent_id: return None
			torrent_files = torrent_files[info_hash]['rd']
			for item in torrent_files:
				video_only = self.video_only(item, extensions)
				if not video_only: continue
				torrent_keys = item.keys()
				if len(torrent_keys) == 0: continue
				append(torrent_keys)
			video_only_items = max(video_only_items, key=len)
			torrent_keys = ','.join(video_only_items)
			self.add_torrent_select(torrent_id, torrent_keys)
			torrent_info = self.torrent_info(torrent_id)
			list_file_items = [dict(i, **{'link':torrent_info['links'][idx]}) for idx, i in enumerate([i for i in torrent_info['files'] if i['selected'] == 1])]
			list_file_items = [{'link': i['link'], 'filename': i['path'].replace('/', ''), 'size': float(i['bytes']) / 1073741824} for i in list_file_items]
			self.delete_torrent(torrent_id)
			return list_file_items
		except:
			log_utils.error('Real-Debrid Error: DISPLAY MAGNET PACK %s : ' % magnet_url)
			if torrent_id: self.delete_torrent(torrent_id)

	def torrents_activeCount(self):
		return self._get(torrents_active_url)

	def add_uncached_torrent(self, magnet_url, pack=False):
		def _return_failed(message=getLS(33586)):
			try: control.progressDialog.close()
			except: pass
			self.delete_torrent(torrent_id)
			control.hide()
			control.sleep(500)
			control.okDialog(title=getLS(40018), message=message)
			return False
		control.busy()
		try:
			active_count = self.torrents_activeCount()
			if active_count['nb'] >= active_count['limit']: return _return_failed()
		except: pass
		interval = 5
		stalled = ['magnet_error', 'error', 'virus', 'dead']
		extensions = supported_video_extensions()
		torrent_id = self.add_magnet(magnet_url)
		if not torrent_id: return _return_failed()
		torrent_info = self.torrent_info(torrent_id)
		if 'error_code' in torrent_info: return _return_failed()
		status = torrent_info['status']
		line = '%s\n%s\n%s'
		if status == 'magnet_conversion':
			line1 = getLS(40013)
			line2 = torrent_info['filename']
			line3 = getLS(40012) % str(torrent_info['seeders'])
			timeout = 100
			control.progressDialog.create(getLS(40018), line % (line1, line2, line3))
			while status == 'magnet_conversion' and timeout > 0:
				control.progressDialog.update(timeout, line % (line1, line2, line3))
				if control.monitor.abortRequested(): return sysexit()
				try:
					if control.progressDialog.iscanceled(): return _return_failed(getLS(40014))
				except: pass
				timeout -= interval
				control.sleep(1000 * interval)
				torrent_info = self.torrent_info(torrent_id)
				status = torrent_info['status']
				if any(x in status for x in stalled): return _return_failed()
				line3 = getLS(40012) % str(torrent_info['seeders'])
			try: control.progressDialog.close()
			except: pass
		if status == 'downloaded':
			control.busy()
			return True
		if status == 'magnet_conversion': return _return_failed()
		if any(x in status for x in stalled): return _return_failed(status)
		if status == 'waiting_files_selection': 
			video_files = []
			append = video_files.append
			all_files = torrent_info['files']
			for item in all_files:
				if any(item['path'].lower().endswith(x) for x in extensions): append(item)
			if pack:
				try:
					if len(video_files) == 0: return _return_failed()
					video_files.sort(key=lambda x: x['path'])
					torrent_keys = [str(i['id']) for i in video_files]
					if not torrent_keys: return _return_failed(getLS(40014))
					torrent_keys = ','.join(torrent_keys)
					self.add_torrent_select(torrent_id, torrent_keys)
					control.okDialog(title='default', message=getLS(40017) % getLS(40058))
					control.hide()
					return True # returning true here causes "success" to be returned and resolve runs on  non valid link
				except: return _return_failed()
			else:
				try:
					video = max(video_files, key=lambda x: x['bytes'])
					file_id = video['id']
				except ValueError: return _return_failed()
				self.add_torrent_select(torrent_id, str(file_id))
			control.sleep(2000)
			torrent_info = self.torrent_info(torrent_id)
			status = torrent_info['status']
			if status == 'downloaded':
				control.hide()
				control.notification(message=getLS(32057), icon=rd_icon)
				return True
			file_size = round(float(video['bytes']) / (1000 ** 3), 2)
			line1 = '%s...' % (getLS(40017) % getLS(40058))
			line2 = torrent_info['filename']
			line3 = status
			control.progressDialog.create(getLS(40018), line % (line1, line2, line3))
			while not status == 'downloaded':
				control.sleep(1000 * interval)
				torrent_info = self.torrent_info(torrent_id)
				status = torrent_info['status']
				if status == 'downloading':
					line3 = getLS(40011) % (file_size, round(float(torrent_info['speed']) / (1000**2), 2), torrent_info['seeders'], torrent_info['progress'])
				else:
					line3 = status
				control.progressDialog.update(int(float(torrent_info['progress'])), line % (line1, line2, line3))
				if control.monitor.abortRequested(): return sysexit()
				try:
					if control.progressDialog.iscanceled():
						if control.yesnoDialog('Delete RD download also?', 'No will continue the download', 'but close dialog'):
							return _return_failed(getLS(40014))
						else:
							control.progressDialog.close()
							control.hide()
							return False
				except: pass
				if any(x in status for x in stalled): return _return_failed()
			try: control.progressDialog.close()
			except: pass
			control.hide()
			return True
		control.hide()
		return False

	def torrent_info(self, torrent_id):
		try:
			url = torrents_info_url + "/%s" % torrent_id
			return self._get(url)
		except:
			log_utils.error('Real-Debrid Error: TORRENT INFO %s : ' % torrent_id)
			return None

	def add_magnet(self, magnet):
		try:
			data = {'magnet': magnet}
			response = self._post(add_magnet_url, data)
			log_utils.log('Real-Debrid: Sending MAGNET URL %s to the Real-Debrid cloud' % magnet, __name__, log_utils.LOGDEBUG)
			return response.get('id', "")
		except:
			log_utils.error('Real-Debrid Error: ADD MAGNET %s : ' % magnet)
			return None

	def add_torrent_select(self, torrent_id, file_ids):
		try:
			url = '%s/%s' % (select_files_url, torrent_id)
			data = {'files': file_ids}
			return self._post(url, data)
		except:
			log_utils.error('Real-Debrid Error: ADD SELECT FILES %s : ' % torrent_id)
			return None

	# def add_torrent_select(self, torrent_id, file_ids=None):
		# try:
			# url = '%s/%s' % (select_files_url, torrent_id)
			# if file_ids == None:
				# extensions = supported_video_extensions()
				# info = self.torrent_info(torrent_id)
				# files = info['files']
				# file_ids = [str(item['id']) for item in files if item['path'].lower().endswith(tuple(extensions))]
				# file_ids = ','.join(file_ids)
			# data = {'files': file_ids}
			# return self._post(url, data)
		# except:
			# log_utils.error('Real-Debrid Error: ADD SELECT FILES %s : ' % torrent_id)
			# return None

	def create_transfer(self, magnet_url):
		try:
			extensions = supported_video_extensions()
			torrent_id = self.add_magnet(magnet_url)
			info = self.torrent_info(torrent_id)
			files = info['files']
			torrent_keys = [str(item['id']) for item in files if item['path'].lower().endswith(tuple(extensions))]
			torrent_keys = ','.join(torrent_keys)
			self.add_torrent_select(torrent_id, torrent_keys)
			return 'success'
		except:
			log_utils.error()
			self.delete_torrent(torrent_id)
			return 'failed'

	def unrestrict_link(self, link):
		post_data = {'link': link}
		response = self._post(unrestrict_link_url, post_data)
		try: return response['download']
		except: return None

	def delete_torrent(self, torrent_id):
		try:
			ck_token = self._get('user', token_ck=True) # check token, and refresh if needed
			url = torrents_delete_url + "/%s&auth_token=%s" % (torrent_id, self.token)
			response = requests.delete(rest_base_url + url)
			log_utils.log('Real-Debrid: Torrent ID %s was removed from your active torrents' % torrent_id, __name__, log_utils.LOGDEBUG)
			return True
		except:
			log_utils.error('Real-Debrid Error: DELETE TORRENT %s : ')

	def get_link(self, link):
		if 'download' in link:
			if 'quality' in link: label = '[%s] %s' % (link['quality'], link['download'])
			else: label = link['download']
			return label, link['download']

	def video_only(self, storage_variant, extensions):
		return False if len([i for i in storage_variant.values() if not i['filename'].lower().endswith(tuple(extensions))]) > 0 else True

	def m2ts_check(self, folder_details):
		for item in folder_details:
			if any(i['filename'].endswith('.m2ts') for i in item.values()): return True
		return False

	def m2ts_key_value(self, torrent_files):
		total_max_size, total_min_length = 0, 10000000000
		for item in torrent_files:
			max_filesize, item_length = max([i['filesize'] for i in item.values()]), len(item)
			if max_filesize >= total_max_size:
				if item_length < total_min_length:
					total_max_size, total_min_length = max_filesize, item_length
					dict_item = item
					key = int([k for k,v in iter(item.items()) if v['filesize'] == max_filesize][0])
		return key, [dict_item,]

	def get_aliases(self, title):
		try: from sqlite3 import dbapi2 as database
		except ImportError: from pysqlite2 import dbapi2 as database
		aliases = []
		try:
			dbcon = database.connect(control.providercacheFile, timeout=60)
			dbcur = dbcon.cursor()
			fetch = dbcur.execute('''SELECT * FROM rel_aliases WHERE title=?''', (title,)).fetchone()
			aliases = eval(fetch[1])
		except:
			log_utils.error()
		return aliases

	def valid_url(self, host):
		try:
			self.hosts = self.get_hosts()
			if not self.hosts['Real-Debrid']: return False
			if any(host in item for item in self.hosts['Real-Debrid']): return True
			return False
		except:
			log_utils.error()

	def get_hosts(self):
		hosts_dict = {'Real-Debrid': []}
		try:
			result = cache.get(self._get, 168, hosts_domains_url)
			hosts_dict['Real-Debrid'] = result
		except:
			log_utils.error()
		return hosts_dict

	def get_hosts_regex(self):
		hosts_regexDict = {'Real-Debrid': []}
		try:
			result = cache.get(self._get, 168, hosts_regex_url)
			hosts_regexDict['Real-Debrid'] = result
		except:
			log_utils.error()
		return hosts_regexDict

	def refresh_token(self):
		try:
			self.client_ID = getSetting('realdebrid.client_id')
			self.secret = getSetting('realdebrid.secret')
			self.device_code = getSetting('realdebrid.refresh')
			if not self.client_ID or not self.secret or not self.device_code: return False # avoid if previous refresh attempt revoked accnt, loops twice.
			log_utils.log('Refreshing Expired Real Debrid Token: | %s | %s |' % (self.client_ID, self.device_code), level=log_utils.LOGDEBUG)
			success, error = self.get_token()
			if not success:
				if not 'Temporarily Down For Maintenance' in error:
					if any(value == error.get('error_code') for value in (9, 12, 13, 14)):
						self.reset_authorization() # empty all auth settings to force a re-auth on next use
						if self.server_notifications: control.notification(message='Real-Debrid Auth revoked due to:  %s' % error.get('error'), icon=rd_icon)
				log_utils.log('Unable to Refresh Real Debrid Token: %s' % error.get('error'), level=log_utils.LOGWARNING)
				return False
			else:
				log_utils.log('Real Debrid Token Successfully Refreshed', level=log_utils.LOGDEBUG)
				return True
		except:
			log_utils.error()
			return False

	def get_token(self):
		try:
			url = oauth_base_url + 'token'
			postData = {'client_id': self.client_ID, 'client_secret': self.secret, 'code': self.device_code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
			response = requests.post(url, data=postData)
			# log_utils.log('Authorizing Real Debrid Result: | %s |' % response, level=log_utils.LOGDEBUG)
			if '[204]' in str(response): return False, str(response)
			if 'Temporarily Down For Maintenance' in response.text:
				if self.server_notifications: control.notification(message='Real-Debrid Temporarily Down For Maintenance', icon=rd_icon)
				log_utils.log('Real-Debrid Temporarily Down For Maintenance', level=log_utils.LOGWARNING)
				return False, response.text
			else: response = response.json()

			if 'error' in response:
				message = response.get('error')
				if self.server_notifications: control.notification(message=message, icon=rd_icon)
				log_utils.log('Real-Debrid Error:  %s' % message, level=log_utils.LOGWARNING)
				return False, response

			self.token = response['access_token']
			control.sleep(500)
			account_info = self.account_info()
			username = account_info['username']
			control.setSetting('realdebrid.username', username)
			control.setSetting('realdebrid.client_id', self.client_ID)
			control.setSetting('realdebrid.secret', self.secret,)
			control.setSetting('realdebrid.token', self.token)
			control.addon('script.module.myaccounts').setSetting('realdebrid.token', self.token)
			control.setSetting('realdebrid.refresh', response['refresh_token'])
			return True, None
		except:
			log_utils.error('Real Debrid Authorization Failed : ')
			return False, None

	def reset_authorization(self):
		try:
			control.setSetting('realdebrid.client_id', '')
			control.setSetting('realdebrid.secret', '')
			control.setSetting('realdebrid.token', '')
			control.setSetting('realdebrid.refresh', '')
			control.setSetting('realdebrid.username', '')
			control.dialog.ok(getLS(40058), getLS(32320))
		except:
			log_utils.error()