# -*- coding: utf-8 -*-
# created by Venom (updated 7-04-2021)
"""
	Venom Add-on
"""

import re
from resources.lib.cloud_scrapers import cloud_utils
from resources.lib.debrid import alldebrid
from resources.lib.modules.control import setting as getSetting
from resources.lib.modules.source_utils import supported_video_extensions
from fenomscrapers.modules import source_utils as fs_utils


class source:
	def __init__(self):
		self.priority = 0 # force cloud scraper to run first
		self.language = ['en']
		self.movie = True
		self.tvshow = True

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		try:
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			aliases = data['aliases']

			episode_title = data['title'] if 'tvshowtitle' in data else None
			self.year = data['year']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else self.year

			self.season = str(data['season']) if 'tvshowtitle' in data else None
			self.episode = str(data['episode']) if 'tvshowtitle' in data else None
			query_list = self.episode_query_list() if 'tvshowtitle' in data else self.year_query_list()
			# log_utils.log('query_list = %s' % query_list)
			try: cloud_folders = alldebrid.AllDebrid().user_cloud()['magnets']
			except: return sources
			if not cloud_folders: return sources
			cloud_folders = [i for i in cloud_folders if i['statusCode'] == 4]
			if not cloud_folders: return sources
			ignoreM2ts = getSetting('ad_cloud.ignore.m2ts') == 'true'
			extras_filter = cloud_utils.extras_filter()
		except:
			from resources.lib.modules import log_utils
			log_utils.error('AD_CLOUD: ')
			return sources

		for folder in cloud_folders:
			is_m2ts = False
			try:
				folder_name = folder.get('filename')
				if not cloud_utils.cloud_check_title(title, aliases, folder_name): continue
				files = folder.get('links', '')
				# files = [i for i in files if i['filename'].lower().endswith(tuple(supported_video_extensions()))]
				if not files: continue
			except:
				from resources.lib.modules import log_utils
				log_utils.error('AD_CLOUD: ')
				return sources

			for file in files:
				try:
					name = file.get('filename', '')
					invalids = ('.rar', '.zip', '.iso', '.part', '.png', '.jpg', '.bmp', '.gif', '.txt', '.srt')
					if name.lower().endswith(invalids): continue
					path = folder.get('filename', '').lower()
					rt = cloud_utils.release_title_format(name)
					if any(value in rt for value in extras_filter): continue

					if '.m2ts' in str(file.get('files')):
						if ignoreM2ts: continue
						if name in str(sources): continue
						if all(not bool(re.search(i, rt)) for i in query_list): continue  # check if this newly added causes any movie titles that do not have the year to get dropped
						is_m2ts = True
						m2ts_files = [i for i in files if name == i.get('filename')]
						largest = sorted(m2ts_files, key=lambda k: k['size'], reverse=True)[0]
						link = largest.get('link', '')
						size =  largest.get('size', '')
					else:
						if all(not bool(re.search(i, rt)) for i in query_list):
							if 'tvshowtitle' in data:
								season_folder_list = self.season_folder_list()
								if all(not bool(re.search(i, path)) for i in season_folder_list): continue
								episode_list = self.episode_list()
								if all(not bool(re.search(i, rt)) for i in episode_list): continue
							else:
								if all(not bool(re.search(i, path)) for i in query_list): continue
								name = folder.get('filename', '')
						link = file.get('link', '')
						size = file.get('size', '')

					name_info = fs_utils.info_from_name(name, title, self.year, hdlr, episode_title)
					hash = folder.get('hash', '')
					seeders = folder.get('seeders', '')
					quality, info = fs_utils.get_release_quality(name_info, name)
					try:
						dsize, isize = fs_utils.convert_size(size, to='GB')
						info.insert(0, isize)
					except: dsize = 0
					if is_m2ts: info.append('M2TS')
					info = ' | '.join(info)

					sources.append({'provider': 'ad_cloud', 'source': 'cloud', 'debrid': 'AllDebrid', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
												'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': True, 'debridonly': True, 'size': dsize})
				except:
					from resources.lib.modules import log_utils
					log_utils.error('AD_CLOUD: ')
					return sources
		return sources

	def year_query_list(self):
		return [str(self.year), str(int(self.year)+1), str(int(self.year)-1)]

	def episode_query_list(self):
		return [
				'[.-]%d[.-]?%02d[.-]' % (int(self.season), int(self.episode)),
				'[.-]%02d[.-]%02d[.-]' % (int(self.season), int(self.episode)),
				'[.-]%dx%02d[.-]' % (int(self.season), int(self.episode)),
				'[.-]%02dx%02d[.-]' % (int(self.season), int(self.episode)),
				's%de%02d' % (int(self.season), int(self.episode)),
				's%02de%02d' % (int(self.season), int(self.episode)),
				'season%depisode%d' % (int(self.season), int(self.episode)),
				'season%depisode%02d' % (int(self.season), int(self.episode)),
				'season%02depisode%02d' % (int(self.season), int(self.episode))]

	def season_folder_list(self):
		return [
				r'[.-]s\s?%d[/]' % int(self.season),
				r'[.-]s\s?%02d[/]' % int(self.season),
				r'season\s?%d[/]' % int(self.season),
				r'season\s?%02d[/]' % int(self.season)]

	def episode_list(self):
		return [
				'[.-]e%d[.-]' % int(self.episode),
				'[.-]e%02d[.-]' % int(self.episode),
				'[.-]ep%d[.-]' % int(self.episode),
				'[.-]ep%02d[.-]' % int(self.episode),
				'episode[.-]?%d[.-]' % int(self.episode),
				'episode[.-]?%02d[.-]' % int(self.episode)]

	def resolve(self, url):
		try:
			url = alldebrid.AllDebrid().unrestrict_link(url)
			return url
		except:
			from resources.lib.modules import log_utils
			log_utils.error('AD_CLOUD: ')
			return None