# coding: utf-8

'''
#:::::::::::::::::::::#
#:'######':'########':#
#::: ## :::::: ## ::::#
#:.. ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#: ###### :::: ## ::::#
#:::::::::::::::::::::#

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re,requests,HTMLParser

def name_clean(name):
	name = HTMLParser.HTMLParser().unescape(name)
	name = name.replace('&quot;', '\"')
	name = name.replace('&amp;', '&')
	name = name.strip()
	return name

def check_quality(quality):
	try:
		quality=quality.lower().replace('p','').replace('-',' ')
		if 'http' in quality:
			if '1080' in quality:
				quality = '1080p'
			elif '720' in quality:
				quality = '720p'
			else:
				quality = 'SD'
		else:
			if '1080' in quality:
				quality = '1080p'
			elif '720' in quality:
				quality = '720p'
			elif 'hd' in quality:
				quality = '720p'
			elif 'blu' in quality:
				quality = '720p'
			elif 'bd' in quality:
				quality = '720p'
			elif 'br' in quality:
				quality = '720p'
			elif 'dvd' in quality:
				quality = '720p'
			else:
				quality = 'SD'

		return quality
	except:
		return 'SD'

def check_site(host):
	try:
		Resolve = [
		'openload',
		'oload',
		'streamango',
		'downace',
		'rapidvideo',
		'vidoza',
		'clicknupload',
		'estream',
		'vidnode',
		'vidzi',
		'putload',
		'blazefile',
		'gorillavid',
		'yourupload',
		'entervideo',
		'youtube',
		'youtu',
		'vimeo',
		'vk',
		'streamcherry',
		'mp4upload',
		'trollvid',
		'vidstreaming',
		'dailymotion',
		'uptostream',
		'uptobox',
		'vidcloud',
		'vcstream',
		'vidto',
		'flashx',
		'thevideo',
		'vshare',
		'vidup'
		]

		Debrid = [
		'1fichier',
		'rapidgator',
		'userscloud',
		'vidlox',
		'filefactory',
		'turbobit',
		'nitroflare'
		]

		if host in Resolve:
			return host+'Resolve'
		elif host in Debrid:
			return host+'Debrid'

		return host
	except:
		return