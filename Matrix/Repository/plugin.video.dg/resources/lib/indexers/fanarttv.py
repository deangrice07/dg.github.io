# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from resources.lib.modules.control import setting as getSetting, apiLanguage, notification

headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
client_key = getSetting('fanart.tv.api.key')
if not client_key: client_key = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
headers.update({'client-key': client_key})
base_url = "http://webservice.fanart.tv/v3/%s/%s"
lang = apiLanguage()['trakt']
error_codes = ('500 Internal Server Error', '502 Bad Gateway', '503 Service Unavailable', '504 Gateway Timeout')
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

def get_request(url):
	try:
		try: result = session.get(url, headers=headers, timeout=5)
		except requests.exceptions.SSLError:
			result = session.get(url, headers=headers, verify=False)
	except requests.exceptions.ConnectionError:
		notification(message='FANART.TV Temporary Server Problems')
		from resources.lib.modules import log_utils
		log_utils.error()
		return None
	try:
		if result.status_code in (200, 201): return result.json()
		elif result.status_code == 404:
			if getSetting('debug.level') == '1':
				from resources.lib.modules import log_utils
				log_utils.log('FANART.TV get_request() failed: (404:NOT FOUND) - URL: %s' % url, level=log_utils.LOGDEBUG)
			return '404:NOT FOUND'
		else:
			if getSetting('debug.level') == '1':
				from resources.lib.modules import log_utils
				from resources.lib.modules.client import parseDOM
				title = parseDOM(result.text, 'title')[0]
				log_utils.log('FANART.TV get_request() failed - URL: %s (%s)' % (url, title), level=log_utils.LOGDEBUG)
			return None
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None

def parse_art(img):
	if not img: return None
	ret_img = []
	try:
		ret_img = [(x['url'], x['likes']) for x in img if x.get('lang') == lang]
		if len(ret_img) >1: ret_img = sorted(ret_img, key=lambda x: int(x[1]), reverse=True)
		elif len(ret_img) == 1: pass
		else:
			ret_img = [(x['url'], x['likes']) for x in img if any(value == x.get('lang') for value in ('en', '00', ''))]
			if len(ret_img) >1: ret_img = sorted(ret_img, key=lambda x: int(x[1]), reverse=True)
		if not ret_img: return None
		ret_img = [x[0] for x in ret_img][0]
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None
	return ret_img

def get_movie_art(imdb, tmdb):
	if not imdb and not tmdb: return None
	art = get_request(base_url % ('movies', tmdb))
	if art is None or '404:NOT FOUND' in art:
		if imdb: art = get_request(base_url % ('movies', imdb))
	if art is None: return None
	elif '404:NOT FOUND' in art: return art
	try:
		if 'movieposter' not in art: raise Exception()
		poster2 = parse_art(art['movieposter'])
	except: poster2 = ''
	try:
		if 'moviebackground' in art: fanart2 = art['moviebackground']
		else:
			if 'moviethumb' not in art: raise Exception()
			fanart2 = art['moviethumb']
		fanart2 = parse_art(fanart2)
	except: fanart2 = ''
	try:
		if 'moviebanner' not in art: raise Exception()
		banner2 = parse_art(art['moviebanner'])
	except: banner2 = ''
	try:
		if 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
		else:
			if 'movielogo' not in art: raise Exception()
			clearlogo = art['movielogo']
		clearlogo = parse_art(clearlogo)
	except: clearlogo = ''
	try:
		if 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
		else:
			if 'movieart' not in art: raise Exception()
			clearart = art['movieart']
		clearart = parse_art(clearart)
	except: clearart = ''
	try:
		if 'moviedisc' not in art: raise Exception()
		discart = parse_art(art['moviedisc'])
	except: discart = ''
	try:
		if 'moviethumb' in art: landscape = art['moviethumb']
		else:
			if 'moviebackground' not in art: raise Exception()
			landscape = art['moviebackground']
		landscape = parse_art(landscape)
	except: landscape = ''
	try:
		keyart = art['movieposter']
		keyart = [(x['url'], x['likes']) for x in keyart if any(value == x.get('lang') for value in ('00', 'None', None))]
		if len(keyart) >1:keyart = sorted(keyart, key=lambda x: int(x[1]), reverse=True)
		keyart = [x[0] for x in keyart][0]
	except: keyart = ''
	extended_art = {'extended': True, 'poster2': poster2, 'fanart2': fanart2, 'banner2': banner2, 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'landscape': landscape, 'keyart': keyart}
	return extended_art

def get_tvshow_art(tvdb):
	if not tvdb: return None
	art = get_request(base_url % ('tv', tvdb))
	if not art: return None
	elif '404:NOT FOUND' in art: return art
	try:
		if 'tvposter' not in art: raise Exception()
		poster2 = parse_art(art['tvposter'])
	except: poster2 = ''
	try: # cache all season_posters and pull from seperate method call at season level
		if 'seasonposter' not in art: raise Exception()
		season_posters = art['seasonposter']
	except: season_posters = ''
	try:
		if 'showbackground' not in art: raise Exception()
		fanart2 = parse_art(art['showbackground'])
	except: fanart2= ''
	try:
		if 'tvbanner' not in art: raise Exception()
		banner2 = parse_art(art['tvbanner'])
	except: banner2 = ''
	try:
		if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
		else:
			if 'clearlogo' not in art: raise Exception()
			clearlogo = art['clearlogo']
		clearlogo = parse_art(clearlogo)
	except: clearlogo = ''
	try:
		if 'hdclearart' in art: clearart = art['hdclearart']
		else:
			if 'clearart' not in art: raise Exception()
			clearart = art['clearart']
		clearart = parse_art(clearart)
	except: clearart = ''
	try:
		if 'tvthumb' in art: landscape = art['tvthumb']
		else:
			if 'showbackground' not in art: raise Exception()
			landscape = art['showbackground']
		landscape = parse_art(landscape)
	except: landscape = ''
	extended_art = {'extended': True, 'poster2': poster2, 'banner2': banner2, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape, 'season_posters': season_posters}
	return extended_art

def get_season_poster(tvdb, season):
	if not tvdb or not season: return None
	try:
		from resources.lib.database import fanarttv_cache
		extended_art = fanarttv_cache.get(get_tvshow_art, 168, tvdb)
		if not extended_art: return None
		season_posters = extended_art.get('season_posters', {})
		if season_posters:
			season_posters = [i for i in season_posters if i.get('season') == str(season)]
			season_poster = parse_art(season_posters)
			return season_poster
	except:
		from resources.lib.modules import log_utils
		log_utils.error()