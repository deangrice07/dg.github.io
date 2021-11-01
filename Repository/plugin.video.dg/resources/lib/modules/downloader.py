# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import os
import re
from urllib.parse import parse_qsl, urlparse
from urllib.request import urlopen, Request
from resources.lib.modules import control
from resources.lib.modules import log_utils
# from resources.lib.modules.source_utils import supported_video_extensions


def download(name, image, url, meta_name=None):
# def download(name, image, url, meta_name=None, selected_source): # future for re-write, pack file support
	if not url: return control.hide()
	try:
		file_format = control.setting('downloads.file.format')
		try: headers = dict(parse_qsl(url.rsplit('|', 1)[1]))
		except: headers = dict('')
		url = url.split('|')[0]
		try: transname = name.translate(None, '\/:*?"<>|').strip('.')
		except: transname = name.translate(name.maketrans('', '', '\/:*?"<>|')).strip('.')  # maketrans() is in string module for py2
		ext_list = ['.m4v', '.mp4', '.mpg', '.mkv', '.flv', '.avi', 'wmv']
		for i in ext_list: transname = transname.rstrip(i)
		if meta_name:
			try: content = re.search(r'(.+?)\sS(\d*)E\d*$', meta_name).groups()
			except: content = ()
			if file_format == '0':
				try: transname = meta_name.translate(None, '\/:*?"<>|').strip('.')
				except: transname = meta_name.translate(meta_name.maketrans('', '', '\/:*?"<>|')).strip('.')
		else:
			try: content = re.search(r'(.+?)(?:|\.| - |-|.-.|\s)(?:S|s|\s|\.)(\d{1,2})(?!\d)(?:|\.| - |-|.-.|x|\s)(?:E|e|\s|.)([0-2]{1}[0-9]{1})(?!\w)', name.replace('\'', '')).groups()
			except: content = ()
		levels =['../../../..', '../../..', '../..', '..']
		if len(content) == 0:
			dest = control.transPath(control.setting('movie.download.path'))
			for level in levels:
				try: control.makeFile(os.path.abspath(os.path.join(dest, level)))
				except: pass
			control.makeFile(dest)
			if meta_name:
				try: dest = os.path.join(dest, meta_name.translate(None, '\/:*?"<>|').strip('.'))
				except: dest = os.path.join(dest, meta_name.translate(meta_name.maketrans('', '', '\/:*?"<>|')).strip('.'))
			else:
				try: movie_info = re.search(r'(.+?)(?:\.{0,1}-{0,1}\.{0,1}|\s*)(?:|\(|\[|\.)((?:19|20)(?:[0-9]{2}))', name.replace('\'', '')).groups()
				except: movie_info = ()
				if len(movie_info) != 0:
					movietitle = titlecase(re.sub(r'[^A-Za-z0-9\s]+', ' ', movie_info[0]))
					dest = os.path.join(dest, movietitle + ' (' + movie_info[1] + ')')
					if file_format == '0':
						transname = movietitle + ' (' + movie_info[1] + ')'
				else:
					dest = os.path.join(dest, transname)
			control.makeFile(dest)
		else:
			dest = control.transPath(control.setting('tv.download.path'))
			for level in levels:
				try: control.makeFile(os.path.abspath(os.path.join(dest, level)))
				except: pass
			control.makeFile(dest)
			try: transtvshowtitle = content[0].translate(None, '\/:*?"<>|').strip('.').replace('.', ' ')
			except: transtvshowtitle = content[0].translate(content[0].maketrans('', '', '\/:*?"<>|')).strip('.').replace('.', ' ')
			if not meta_name:
				transtvshowtitle = titlecase(re.sub(r'[^A-Za-z0-9\s-]+', ' ', transtvshowtitle))
			dest = os.path.join(dest, transtvshowtitle)
			control.makeFile(dest)
			dest = os.path.join(dest, 'Season %01d' % int(content[1]))
			control.makeFile(dest)
			if file_format == '0' and not meta_name:
				transname = transtvshowtitle + ' S%sE%s' % (content[1], content[2])
		ext = os.path.splitext(urlparse(url).path)[1][1:]
		if not ext in ['.m4v', '.mp4', '.mpg', '.mkv', '.flv', '.avi', 'wmv']:
			ext = 'mp4'
		dest = os.path.join(dest, transname + '.' + ext)
		doDownload(url, dest, name, image, headers)
	except:
		log_utils.error()

def getResponse(url, headers, size):
	try:
		if size > 0:
			size = int(size)
			headers['Range'] = 'bytes=%d-' % size
		req = Request(url, headers=headers)
		resp = urlopen(req, timeout=30)
		return resp
	except:
		log_utils.error()
		return None

def done(title, dest, downloaded):
	try:
		playing = control.player.isPlaying()
		text = control.homeWindow.getProperty('GEN-DOWNLOADED')
		# if len(text) > 0: text += '[CR]'
		if len(text) > 0: text += '\n'
		if downloaded:
			text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR forestgreen]Download succeeded[/COLOR]')
		else:
			text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR red]Download failed[/COLOR]')
		control.homeWindow.setProperty('GEN-DOWNLOADED', text)
		if (not downloaded) or (not playing): 
			control.okDialog(title, text)
			control.homeWindow.clearProperty('GEN-DOWNLOADED')
	except:
		log_utils.error()

def doDownload(url, dest, title, image, headers):
	file = dest.rsplit(os.sep, 1)[-1]
	resp = getResponse(url, headers, 0)
	if not resp:
		control.hide()
		return control.okDialog(title, dest + 'Download failed: No response from server')
	try: content = int(resp.headers['Content-Length'])
	except: content = 0
	try: resumable = 'bytes' in resp.headers['Accept-Ranges'].lower()
	except: resumable = False
	if content < 1:
		control.hide()
		return control.okDialog(title, file + 'Unknown filesize: Unable to download')
	size = 1024 * 1024
	gb = str(round(content / float(1073741824), 2))
	if content < size:
		size = content
	total = 0
	notify = 0
	errors = 0
	count = 0
	resume = 0
	sleep = 0
	control.hide()
	if control.yesnoDialog('File Size: %sGB\nPath: %s\nContinue with download?' % (gb, dest), '', '', 'Confirm Download', 'Confirm',  'Cancel') == 1: return
	f = control.openFile(dest, 'w')
	chunk  = None
	chunks = []
	import xbmcgui
	while True:
		downloaded = total
		for c in chunks: downloaded += len(c)
		percent = min(100 * downloaded / content, 100)
		if percent >= notify:
			control.notification(title=title + ' - Download Progress - ' + str(int(percent)) + '%', message='', icon=image, time=3000) #xbmcgui.Dialog().notification() auto scroll time to complete supercedes allowed "time=" to run in Silvo, removed dest
			notify += 20
		chunk = None
		error = False
		try:
			chunk  = resp.read(size)
			if not chunk:
				if percent < 99: error = True
				else:
					while len(chunks) > 0:
						c = chunks.pop(0)
						f.write(c)
						del c
					f.close()
					log_utils.log('Download Complete: %s' % (dest), level=log_utils.LOGDEBUG)
					return done(title, dest, True)
		except:
			log_utils.error('DOWNNLOADER EXCEPTION: ')
			error = True
			sleep = 10
			errno = 0
			if hasattr(e, 'errno'):
				errno = e.errno
			if errno == 10035: # 'A non-blocking socket operation could not be completed immediately'
				pass
			if errno == 10054: #'An existing connection was forcibly closed by the remote host'
				errors = 10 #force resume
				sleep  = 30
			if errno == 11001: # 'getaddrinfo failed'
				errors = 10 #force resume
				sleep  = 30
		if chunk:
			errors = 0
			chunks.append(chunk)
			if len(chunks) > 5:
				c = chunks.pop(0)
				f.write(c)
				total += len(c)
				del c
		if error:
			errors += 1
			count  += 1
			control.sleep(sleep*1000)
		if (resumable and errors > 0) or errors >= 10:
			if (not resumable and resume >= 50) or resume >= 500: # Give up!
				log_utils.log('Download Canceled: %s - too many errors whilst downloading' % (dest), level=log_utils.LOGWARNING)
				return done(title, dest, False)
			resume += 1
			errors  = 0
			if resumable:
				chunks  = []
				resp = getResponse(url, headers, total) # create new response
			else: pass

def titlecase(string): # not perfect but close enough
	try:
		articles = ['a', 'an', 'the', 'vs', 'v']
		word_list = re.split(' ', string)
		sw_num = re.match(r'^(19|20[0-9]{2})', string)
		final = [word_list[0].capitalize()]
		pos = 1
		for word in word_list[1:]:
			final.append(word if word in articles and (not sw_num and pos == 1) else word.capitalize())
			pos += 1
		return " ".join(final)
	except:
		log_utils.error()
		return string