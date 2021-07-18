# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime
import re
import requests # seems faster than urlli2.urlopen
import zipfile
# from urllib.request import urlopen
from urllib.parse import quote_plus
from io import BytesIO
from resources.lib.database import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import log_utils

lang = control.apiLanguage()['tvdb']
api_key = control.setting('tvdb.api.key')
imdb_user = control.setting('imdb.user').replace('ur', '')
user = str(imdb_user) + str(api_key)

baseUrl = 'https://thetvdb.com'
info_link = '%s/api/%s/series/%s/%s.xml' % (baseUrl, api_key, '%s', '%s')
all_info_link = '%s/api/%s/series/%s/all/%s.xml' % (baseUrl, api_key, '%s', '%s')
zip_link = '%s/api/%s/series/%s/all/%s.zip' % (baseUrl, api_key, '%s', '%s')
by_imdb = '%s/api/GetSeriesByRemoteID.php?imdbid=%s' % (baseUrl, '%s')
by_seriesname = '%s/api/GetSeries.php?seriesname=%s' % (baseUrl, '%s')
imageUrl = '%s/banners/' % baseUrl
tvdb_poster = '%s/banners/_cache/' % baseUrl
date_time = datetime.now()
today_date = (date_time).strftime('%Y-%m-%d')
showunaired = control.setting('showunaired') or 'true'
showspecials = control.setting('tv.specials') == 'true'


def getZip(tvdb, art_xml=None, actors_xml=None):
	url = zip_link % (tvdb, lang)
	try:
		# data = urlopen(url, timeout=30).read()
		data = requests.get(url, timeout=30, verify=True).content # test .content vs. .text
		zip = zipfile.ZipFile(BytesIO(data))
		result = zip.read('%s.xml' % lang).decode('utf-8')
		if not art_xml and not actors_xml:
			zip.close()
			return result
		elif art_xml and not actors_xml:
			artwork = zip.read('banners.xml').decode('utf-8')
			zip.close()
			return (result, artwork)
		elif actors_xml and not art_xml:
			actors = zip.read('actors.xml').decode('utf-8')
			zip.close()
			return (result, actors)
		else:
			artwork = zip.read('banners.xml').decode('utf-8')
			actors = zip.read('actors.xml').decode('utf-8')
			zip.close()
			return (result, artwork, actors)
	except:
		log_utils.error()
		return None


def parseAll(tvdb, limit):
	try:
		dupe = client.parseDOM(result, 'SeriesName')[0]
		dupe = re.compile(r'[***]Duplicate (\d*)[***]').findall(dupe)
		if len(dupe) > 0:
			tvdb = str(dupe[0])
			result, artwork, actors = cache.get(getZip, 96, tvdb, True, True)

		# if lang != 'en':
			# url = zip_link % (tvdb, lang)
			# # data = urlopen(url, timeout=30).read()
			# data = requests.get(url, timeout=30).content # test .content vs. .text
			# zip = zipfile.ZipFile(BytesIO(data))
			# result2 = zip.read('%s.xml' % lang)
			# zip.close()
		# else: result2 = result

		artwork = artwork.split('<Banner>')
		artwork = [i for i in artwork if '<Language>en</Language>' in i and '<BannerType>season</BannerType>' in i]
		artwork = [i for i in artwork if not 'seasonswide' in re.findall(r'<BannerPath>(.+?)</BannerPath>', i)[0]]

		result = result.split('<Episode>')
		item = result[0]

		episodes = [i for i in result if '<EpisodeNumber>' in i]
		if control.setting('tv.specials') == 'true':
			episodes = [i for i in episodes]
		else:
			episodes = [i for i in episodes if not '<SeasonNumber>0</SeasonNumber>' in i]
			episodes = [i for i in episodes if not '<EpisodeNumber>0</EpisodeNumber>' in i]

		# season still airing check for pack scraping
		premiered_eps = [i for i in episodes if not '<FirstAired></FirstAired>' in i]
		unaired_eps = [i for i in premiered_eps if int(re.sub(r'[^0-9]', '', str(client.parseDOM(i, 'FirstAired')))) > int(re.sub(r'[^0-9]', '', str(self.today_date)))]
		if unaired_eps: still_airing = client.parseDOM(unaired_eps, 'SeasonNumber')[0]
		else: still_airing = None

		seasons = [i for i in episodes if '<EpisodeNumber>1</EpisodeNumber>' in i]
		counts = seasonCountParse(seasons = seasons, episodes = episodes)
		# locals = [i for i in result2 if '<EpisodeNumber>' in i]

		if limit == '': episodes = []
		elif limit == '-1': seasons = []
		else:
			episodes = [i for i in episodes if '<SeasonNumber>%01d</SeasonNumber>' % int(limit) in i]
			seasons = []

		try: imdb = client.parseDOM(item, 'IMDB_ID')[0] or ''
		except: imdb = ''

		poster = client.replaceHTMLCodes(client.parseDOM(item, 'poster')[0])
		if poster != '': poster = '%s%s' % (self.tvdb_image, poster)

		fanart = client.replaceHTMLCodes(client.parseDOM(item, 'fanart')[0])
		if fanart != '': fanart = '%s%s' % (self.tvdb_image, fanart)

		banner = client.replaceHTMLCodes(client.parseDOM(item, 'banner')[0])
		if banner != '': banner = '%s%s' % (self.tvdb_image, banner)

		if poster != '': pass
		elif fanart != '': poster = fanart
		elif banner != '': poster = banner

		if banner != '': pass
		elif fanart != '': banner = fanart
		elif poster != '': banner = poster

		status = client.replaceHTMLCodes(client.parseDOM(item, 'Status')[0]) or 'Ended'
		studio = client.replaceHTMLCodes(client.parseDOM(item, 'Network')[0]) or ''
		genre = client.replaceHTMLCodes(client.parseDOM(item, 'Genre')[0])
		genre = ' / '.join([x for x in genre.split('|') if x != ''])
		duration = client.replaceHTMLCodes(client.parseDOM(item, 'Runtime')[0])
		rating = client.replaceHTMLCodes(client.parseDOM(item, 'Rating')[0])
		votes = client.replaceHTMLCodes(client.parseDOM(item, 'RatingCount')[0])
		mpaa = client.replaceHTMLCodes(client.parseDOM(item, 'ContentRating')[0])
		castandart = parseActors(actors)
		label = client.replaceHTMLCodes(client.parseDOM(item, 'SeriesName')[0])
		plot = client.replaceHTMLCodes(client.parseDOM(item, 'Overview')[0])
	except:
		log_utils.error()

	for item in seasons:
		try:
			premiered = client.replaceHTMLCodes(client.parseDOM(item, 'FirstAired')[0]) or ''
			# Show Unaired items.
			unaired = ''
			if status.lower() == 'ended': pass
			elif premiered == '':
				unaired = 'true'
				if showunaired != 'true': continue
				pass
			elif int(re.sub(r'[^0-9]', '', str(premiered))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
				unaired = 'true'
				if showunaired != 'true': continu

			season = client.parseDOM(item, 'SeasonNumber')[0]
			season = '%01d' % int(season)

			thumb = [i for i in artwork if client.parseDOM(i, 'Season')[0] == season]
			try: thumb = client.replaceHTMLCodes(client.parseDOM(thumb[0], 'BannerPath')[0])
			except: thumb = ''
			if thumb != '': thumb = '%s%s' % (self.tvdb_image, thumb)
			else: thumb = poster

			try: seasoncount = counts[season]
			except: seasoncount = None
			try: total_seasons = len([i for i in counts if i])
			except: total_seasons = None

			list.append({'season': season, 'tvshowtitle': tvshowtitle, 'label': label, 'year': year, 'premiered': premiered,
							'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
							'mpaa': mpaa, 'castandart': castandart, 'plot': plot, 'imdb': imdb, 'tmdb': '', 'tvdb': tvdb,
							'tvshowid': imdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb,
							'unaired': unaired, 'seasoncount': seasoncount, 'total_seasons': total_seasons})
			list = sorted(self.list, key=lambda k: int(k['season'])) # fix for TVDb new sort by ID
		except:
			log_utils.error()

	for item in episodes:
		try:
			title = client.replaceHTMLCodes(client.parseDOM(item, 'EpisodeName')[0])
			premiered = client.replaceHTMLCodes(client.parseDOM(item, 'FirstAired')[0]) or ''
			# Show Unaired items.
			unaired = ''
			if status.lower() == 'ended': pass
			elif premiered == '':
				unaired = 'true'
				if showunaired != 'true': continue
				pass
			elif int(re.sub(r'[^0-9]', '', str(premiered))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
				unaired = 'true'
				if showunaired != 'true': continue

			season = client.parseDOM(item, 'SeasonNumber')[0]
			season = '%01d' % int(season)
			episode = client.parseDOM(item, 'EpisodeNumber')[0]
			episode = re.sub(r'[^0-9]', '', '%01d' % int(episode))

# ### episode IDS
			episodeIDS = {}
			if control.setting('enable.playnext') == 'true':
				episodeIDS = trakt.getEpisodeSummary(imdb, season, episode, full=False) or {}
				if episodeIDS != {}:
					episodeIDS = episodeIDS.get('ids', {})
##------------------

			thumb = client.replaceHTMLCodes(client.parseDOM(item, 'filename')[0])
			if thumb != '': thumb = '%s%s' % (self.tvdb_image, thumb)

			season_poster = [i for i in artwork if client.parseDOM(i, 'Season')[0] == season]
			try: season_poster = client.replaceHTMLCodes(client.parseDOM(season_poster[0], 'BannerPath')[0])
			except: season_poster = ''
			if season_poster != '': season_poster = '%s%s' % (self.tvdb_image, season_poster)
			else: season_poster = poster

			if thumb != '': pass
			elif fanart != '': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
			elif season_poster != '': thumb = season_poster

			rating = client.replaceHTMLCodes(client.parseDOM(item, 'Rating')[0])
			director = client.replaceHTMLCodes(client.parseDOM(item, 'Director')[0])
			director = ' / '.join([x for x in director.split('|') if x != ''])
			writer = client.replaceHTMLCodes(client.parseDOM(item, 'Writer')[0]) 
			writer = ' / '.join([x for x in writer.split('|') if x != ''])
			label = client.replaceHTMLCodes(client.parseDOM(item, 'EpisodeName')[0])

			episodeplot = client.replaceHTMLCodes(client.parseDOM(item, 'Overview')[0]) or plot

			try: seasoncount = counts[season]
			except: seasoncount = None
			try: total_seasons = len([i for i in counts if i])
			except: total_seasons = None


			list.append({'title': title, 'label': label, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year,
								'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating,
								'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'castandart': castandart, 'plot': episodeplot,
								'imdb': imdb, 'tmdb': '', 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb,
								'season_poster': season_poster, 'unaired': unaired, 'seasoncount': seasoncount, 'counts': counts,
								'total_seasons': total_seasons, 'season_isAiring': season_isAiring, 'episodeIDS': episodeIDS})
			list = sorted(list, key=lambda k: (int(k['season']), int(k['episode']))) # fix for TVDb new sort by ID
			# meta = {}
			# meta = {'imdb': imdb, 'tmdb': '', 'tvdb': tvdb, 'lang': lang, 'user': user, 'item': item}
			# list.append(item)
			# metacache.insert(meta)
		except:
			log_utils.error()
	return list


def parseSeasonPoster(artwork, season):
	try:
		season_poster = [x for x in artwork if client.parseDOM(x, 'Season')[0] == season]
		season_poster = client.parseDOM(season_poster[0], 'BannerPath')[0]
		season_poster = imageUrl + season_poster or None
		season_poster = client.replaceHTMLCodes(season_poster)
		return season_poster
	except:
		log_utils.error()
		return None


def getSeries_by_id(tvdb):
	url = info_link % (tvdb, lang)
	items = []
	try:
		item = client.request(url, timeout='10', error = True)
		if item is None: raise Exception()
		try: imdb = client.parseDOM(item, 'IMDB_ID')[0] or ''
		except: imdb = ''

		title = client.replaceHTMLCodes(client.parseDOM(item, 'SeriesName')[0])

		year = client.parseDOM(item, 'FirstAired')[0]
		year = re.compile(r'(\d{4})').findall(year)[0]
		premiered = client.parseDOM(item, 'FirstAired')[0]

		studio = client.parseDOM(item, 'Network')[0]

		genre = client.parseDOM(item, 'Genre')[0]
		genre = [x for x in genre.split('|') if x != '']
		genre = ' / '.join(genre)

		duration = client.parseDOM(item, 'Runtime')[0]
		rating = client.parseDOM(item, 'Rating')[0]
		votes = client.parseDOM(item, 'RatingCount')[0]
		mpaa = client.parseDOM(item, 'ContentRating')[0]

		plot = client.replaceHTMLCodes(client.parseDOM(item, 'Overview')[0])

		status = client.parseDOM(item, 'Status')[0]
		if not status: status = 'Ended'

		poster = client.parseDOM(item, 'poster')[0]
		poster = '%s%s' % (imageUrl, poster ) if poster else ''

		banner = client.parseDOM(item, 'banner')[0]
		banner = '%s%s' % (imageUrl, banner) if banner else ''

		fanart = client.parseDOM(item, 'fanart')[0]
		fanart = '%s%s' % (imageUrl, fanart) if fanart else ''

		items.append({'extended': True, 'title': title, 'year': year, 'imdb': imdb, 'tmdb': '', 'tvdb': tvdb, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration,
					'rating': rating, 'votes': votes, 'mpaa': mpaa, 'castandart': castandart, 'plot': plot, 'status': status, 'poster': poster, 'poster2': '', 'poster3': '', 'banner': banner,
					'banner2': '', 'fanart': fanart, 'fanart2': '', 'fanart3': '', 'clearlogo': '', 'clearart': '', 'landscape': fanart, 'metacache': False})
		# meta = {'imdb': imdb, 'tmdb': '', 'tvdb': tvdb, 'lang': lang, 'user': user, 'item': items}
		return items
	except:
		log_utils.error()
		return None


def getBanners(tvdb):
	url = info_link % (tvdb, 'banners')
	try:
		artwork = client.request(url, timeout='10', error=True)
		if artwork is None: raise Exception()
		artwork = artwork.split('<Banner>')
		artwork = [i for i in artwork if '<Language>en</Language>' in i and '<BannerType>season</BannerType>' in i]
		artwork = [i for i in artwork if not 'seasonswide' in re.findall(r'<BannerPath>(.+?)</BannerPath>', i)[0]]
		return artwork
	except:
		log_utils.error()
		return None


# def parseBanners(artwork):


def getActors(tvdb):
	actors = None
	try:
		url = info_link % (tvdb, 'actors')
		actors = client.request(url, timeout='10', error=True)
	except:
		log_utils.error()
	return actors


def parseActors(actors):
	castandart = []
	try:
		if not actors: return castandart
		import xml.etree.ElementTree as ET
		tree = ET.ElementTree(ET.fromstring(actors))
		root = tree.getroot()
		for actor in root.iter('Actor'):
			person = [name.text for name in actor]
			image = person[1]
			name = client.replaceHTMLCodes(person[2]) or ''
			role = client.replaceHTMLCodes(person[3]) or ''
			try: castandart.append({'name': name, 'role': role, 'thumbnail': ((imageUrl + image) if image else '')})
			except: pass
			if len(castandart) == 150: break # cast seems to have a limit and a show like "Survivor" has 500+ actors and breaks
		return castandart
	except:
		log_utils.error()
		return []


def getSeries_ByIMDB(title, year, imdb):
	try:
		url = by_imdb % imdb
		result = client.request(url, timeout='10')
		# result = requests.get(url, timeout=10).content # test .content vs. .text
		# result = result.decode('utf-8')
		result = re.sub(r'[^\x00-\x7F]+', '', result)
		result = client.replaceHTMLCodes(result)
		result = client.parseDOM(result, 'Series')
		result = [(client.parseDOM(x, 'SeriesName'), client.parseDOM(x, 'FirstAired'), client.parseDOM(x, 'seriesid'), client.parseDOM(x, 'AliasNames')) for x in result]
		years = [str(year), str(int(year)+1), str(int(year)-1)]
		item = [(x[0], x[1], x[2], x[3]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[0][0])) and any(y in str(x[1][0]) for y in years)]
		if item == []: item = [(x[0], x[1], x[2], x[3]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[3][0]))]
		if item == []: item = [(x[0], x[1], x[2], x[3]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[0][0]))]
		if item == []: return ''
		tvdb = item[0][2]
		tvdb = tvdb[0] or ''
		return tvdb
	except:
		log_utils.error()
	return ''


def getSeries_ByName(title, year):
	try:
		url = by_seriesname % (quote_plus(title))
		result = client.request(url, timeout='10')
		# result = requests.get(url, timeout=10).content # test .content vs. .text
		# result = result.decode('utf-8')
		result = re.sub(r'[^\x00-\x7F]+', '', result)
		result = client.replaceHTMLCodes(result)
		result = client.parseDOM(result, 'Series')
		result = [(client.parseDOM(x, 'SeriesName'), client.parseDOM(x, 'FirstAired'), client.parseDOM(x, 'seriesid'), client.parseDOM(x, 'IMDB_ID'), client.parseDOM(x, 'AliasNames')) for x in result]
		years = [str(year), str(int(year)+1), str(int(year)-1)]
		item = [(x[0], x[1], x[2], x[3], x[4]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[0][0])) and any(y in str(x[1][0]) for y in years)]
		if item == []: item = [(x[0], x[1], x[2], x[3], x[4]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[4][0]))]
		if item == []: item = [(x[0], x[1], x[2], x[3], x[4]) for x in result if cleantitle.get(title) == cleantitle.get(str(x[0][0]))]
		if item == []: return None
		tvdb = item[0][2]
		tvdb = tvdb[0] or ''
		imdb = item[0][3]
		imdb = imdb[0] or ''
		return {'tvdb': tvdb, 'imdb': imdb}
	except:
		log_utils.error()


def get_season_isAiring(tvdb, season):
	url = all_info_link % (tvdb, lang)
	try:
		# result = client.request(url, timeout='10', as_bytes=True)
		result = client.request(url, timeout='10')
		result = result.split('<Episode>')
		episodes = [i for i in result if '<EpisodeNumber>' in i]
		if control.setting('tv.specials') == 'true':
			episodes = [i for i in episodes]
		else:
			episodes = [i for i in episodes if not '<SeasonNumber>0</SeasonNumber>' in i]
			episodes = [i for i in episodes if not '<EpisodeNumber>0</EpisodeNumber>' in i]
		# season still airing check for pack scraping
		premiered_eps = [i for i in episodes if not '<FirstAired></FirstAired>' in i]
		unaired_eps = [i for i in premiered_eps if int(re.sub(r'[^0-9]', '', str(client.parseDOM(i, 'FirstAired')))) > int(re.sub(r'[^0-9]', '', str(today_date)))]
		if unaired_eps: still_airing = client.parseDOM(unaired_eps, 'SeasonNumber')[0]
		else: still_airing = None
		if still_airing:
			if int(still_airing) == int(season): season_isAiring = True # check as this is now 'true' or 'false' str not bool
			else: season_isAiring = False
		else: season_isAiring = False
		return season_isAiring
	except:
		log_utils.error()


def get_counts(tvdb):
	url = all_info_link % (tvdb, lang)
	try:
		result = client.request(url, timeout='10')
		# result = requests.get(url, timeout=10).content # test .content vs. .text
		# result = result.decode('utf-8')
		result = result.split('<Episode>')
		episodes = [i for i in result if '<EpisodeNumber>' in i]
		if control.setting('tv.specials') == 'true':
			episodes = [i for i in episodes]
		else:
			episodes = [i for i in episodes if not '<SeasonNumber>0</SeasonNumber>' in i]
			episodes = [i for i in episodes if not '<EpisodeNumber>0</EpisodeNumber>' in i]
		seasons = [i for i in episodes if '<EpisodeNumber>1</EpisodeNumber>' in i]
		counts = seasonCountParse(seasons=seasons, episodes=episodes)
		# log_utils.log('counts = %s' % str(counts), __name__, log_utils.LOGDEBUG)
		return counts
	except:
		log_utils.error()


def episodeCountParse(item):
	try:
		split_eps = item.split('<Episode>')
		episodes = [x for x in split_eps if '<EpisodeNumber>' in x]
		if control.setting('tv.specials') == 'true':
			episodes = [x for x in episodes]
		else:
			episodes = [x for x in episodes if not '<SeasonNumber>0</SeasonNumber>' in x]
			episodes = [x for x in episodes if not '<EpisodeNumber>0</EpisodeNumber>' in x]
		unknown_premiered_eps = [x for x in episodes if '<FirstAired></FirstAired>' in x]
		premiered_eps = [x for x in episodes if not '<FirstAired></FirstAired>' in x]
		unaired_eps = [x for x in premiered_eps if int(re.sub(r'[^0-9]', '', str(client.parseDOM(x, 'FirstAired')))) > int(re.sub(r'[^0-9]', '', str(today_date)))]
		total_episodes = len(episodes) - len(unaired_eps) - len(unknown_premiered_eps)
	except:
		log_utils.error()
		total_episodes = ''
	return total_episodes


def seasonCountParse(season=None, items=None, seasons=None, episodes=None):
	# Determine the number of episodes per season to estimate season pack episode sizes.
	index = season
	counts = {} # Do not use a list, since not all seasons are labeled by number. Eg: MythBusters
	if episodes is None:
		episodes = [i for i in items if '<EpisodeNumber>' in i]
		if control.setting('tv.specials') == 'true':
			episodes = [i for i in episodes]
		else:
			episodes = [i for i in episodes if not '<SeasonNumber>0</SeasonNumber>' in i]
			episodes = [i for i in episodes if not '<EpisodeNumber>0</EpisodeNumber>' in i]
		seasons = [i for i in episodes if '<EpisodeNumber>1</EpisodeNumber>' in i]
	for s in seasons:
		season = client.parseDOM(s, 'SeasonNumber')[0]
		season = '%01d' % int(season)
		counts[season] = 0
	for e in episodes:
		try:
			season = client.parseDOM(e, 'SeasonNumber')[0]
			season = '%01d' % int(season)
			counts[season] += 1
		except: pass
	try:
		if index is None: return counts
		else: return counts[index]
	except: return None


def seasonCount(tvshowtitle, year, imdb, tvdb, season):
	try: return cache.get(_seasonCount, 168, tvshowtitle, year, imdb, tvdb)[season]
	except: return None


def _seasonCount(tvshowtitle, year, imdb, tvdb):
	if not imdb:
		try:
			result = trakt.SearchTVShow(quote_plus(tvshowtitle), year, full=False)[0]
			show = result.get('show')
			imdb = show.get('ids', {}).get('imdb', '') if show.get('ids').get('imdb') else ''
		except:
			log_utils.error()
			imdb = ''

	if not tvdb and imdb: # Check TVDb by IMDB_ID for missing id
		try: tvdb = getSeries_ByIMDB(tvshowtitle, year, imdb) or ''
		except: tvdb = ''
	if not tvdb: # Check TVDb by seriesname
		try:
			ids = getSeries_ByName(tvshowtitle, year)
			if ids: tvdb = ids.get(tvdb, '') if ids.get(tvdb) else ''
		except:
			log_utils.error()
			tvdb = ''

	if not tvdb: return None
	try:
		result = getZip(tvdb)
		dupe = client.parseDOM(result, 'SeriesName')[0]
		dupe = re.compile(r'[***]Duplicate (\d*)[***]').findall(dupe)
		if len(dupe) > 0:
			tvdb = str(dupe[0])
			result = getZip(tvdb)
		result = result.split('<Episode>')
		return seasonCountParse(items=result)
	except:
		log_utils.error()
		return None


# ###### -- Original TVDb code from episodes.trakt_progress_list()
# def trakt_progress_list(self, url, user, lang, direct=False):
	# # from resources.lib.menus import seasons
	# try:
		# url += '?extended=full'
		# result = trakt.getTrakt(url)
		# result = jsloads(result)
		# items = []
	# except: return

	# for item in result:
		# try:
			# num_1 = 0
			# for i in range(0, len(item['seasons'])):
				# if item['seasons'][i]['number'] > 0: num_1 += len(item['seasons'][i]['episodes'])
			# num_2 = int(item['show']['aired_episodes'])
			# if num_1 >= num_2: continue

			# season_sort = sorted(item['seasons'][:], key=lambda k: k['number'], reverse=False) # trakt sometimes places season0 at end and episodes out of order. So we sort it to be sure.
			# season = str(season_sort[-1]['number'])
			# episode = [x for x in season_sort[-1]['episodes'] if 'number' in x]
			# episode = sorted(episode, key=lambda x: x['number'])
			# episode = str(episode[-1]['number'])

			# tvshowtitle = item['show']['title']
			# if not tvshowtitle or tvshowtitle == '': continue

			# year = str(item.get('show').get('year'))

			# imdb = str(item.get('show', {}).get('ids', {}).get('imdb', ''))
			# if not imdb or imdb == 'None': imdb = ''
			# tmdb = str(item.get('show', {}).get('ids', {}).get('tmdb', ''))
			# if not tmdb or tmdb == 'None': tmdb = ''
			# tvdb = str(item.get('show', {}).get('ids', {}).get('tvdb', ''))
			# if not tvdb or tvdb == 'None': tvdb = ''

			# try: added = item['show']['updated_at']
			# except: added = None
			# lastplayed = item.get('show').get('last_watched_at') or item.get('last_watched_at')

			# studio = item.get('show').get('network', '0')
			# status = item.get('show').get('status', '0')

			# try: trailer = control.trailer % item['show']['trailer'].split('v=')[1]
			# except: trailer = ''

			# values = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season,
							# 'enum': episode, 'added': added, 'lastplayed': lastplayed, 'studio': studio, 'status': status,
							# 'trailer': trailer}
			# try:
				# air = item['show']['airs']
				# values['airday'] = air['day']
				# values['airtime'] = air['time']
				# values['airzone'] = air['timezone']
			# except: pass
			# items.append(values)
		# except: pass
	# try:
		# result = trakt.getTrakt(self.hiddenprogress_link)
		# result = jsloads(result)
		# result = [str(i['show']['ids']['tvdb']) for i in result]
		# items = [i for i in items if i['tvdb'] not in result] # removes hidden progress items
	# except: pass

	# def items_list(i):
		# tvshowtitle = i['tvshowtitle']
		# year = str(i.get('year'))
		# imdb, tmdb, tvdb = i['imdb'], i['tmdb'], i['tvdb']
		# trailer = i.get('trailer')
		# try:
			# result, artwork, actors = cache.get(getZip, 96, tvdb, True, True)
			# result = result.split('<Episode>')
			# item = [x for x in result if '<EpisodeNumber>' in x]
			# item2 = result[0]

			# try: # TVDB en.xml sort order is by ID now so we resort by season then episode for proper indexing of nextup item to watch.
				# sorted_item = [y for y in item if any(re.compile(r'<SeasonNumber>(.+?)</SeasonNumber>').findall(y)[0] == z for z in [str(i['snum']), str(int(i['snum']) + 1)])]
				# sorted_item = sorted(sorted_item, key= lambda t:(int(re.compile(r'<SeasonNumber>(\d+)</SeasonNumber>').findall(t)[-1]), int(re.compile(r'<EpisodeNumber>(\d+)</EpisodeNumber>').findall(t)[-1])))
				# num = [x for x,y in enumerate(sorted_item) if re.compile(r'<SeasonNumber>(.+?)</SeasonNumber>').findall(y)[0] == str(i['snum']) and re.compile(r'<EpisodeNumber>(.+?)</EpisodeNumber>').findall(y)[0] == str(i['enum'])][-1]
				# item = [y for x,y in enumerate(sorted_item) if x > num][0]
			# except: return

			# artwork = artwork.split('<Banner>')
			# artwork = [x for x in artwork if '<Language>en</Language>' in x and '<BannerType>season</BannerType>' in x]
			# artwork = [x for x in artwork if not 'seasonswide' in re.findall(r'<BannerPath>(.+?)</BannerPath>', x)[0]]

			# premiered = client.parseDOM(item, 'FirstAired')[0]
			# if premiered == '' or '-00' in premiered: premiered = ''

			# try: added = i['added']
			# except: added = None
			# try: lastplayed = i['lastplayed']
			# except: lastplayed = None

			# status = i['status'] or client.parseDOM(item2, 'Status')[0]
			# # Show Unaired items.
			# unaired = ''
			# if status.lower() == 'ended': pass
			# elif premiered == '':
				# unaired = 'true'
				# if self.showunaired != 'true': return
				# pass
			# elif int(re.sub(r'[^0-9]', '', str(premiered))) > int(re.sub(r'[^0-9]', '', str(self.today_date))):
				# unaired = 'true'
				# if self.showunaired != 'true': return

			# title = client.parseDOM(item, 'EpisodeName')[0]
			# title = client.replaceHTMLCodes(title)

			# season = client.parseDOM(item, 'SeasonNumber')[0]
			# season = '%01d' % int(season)

			# if not showspecials and season == '0': raise Exception()

			# episode = client.parseDOM(item, 'EpisodeNumber')[0]
			# episode = re.sub(r'[^0-9]', '', '%01d' % int(episode))

			# episodeIDS = {}
			# if control.setting('enable.playnext') == 'true':
				# episodeIDS = trakt.getEpisodeSummary(imdb, season, episode, full=False) or {}
				# if episodeIDS != {}:
					# episodeIDS = episodeIDS.get('ids', {})

			# total_seasons = ''
			# total_episodes = ''
			# seasoncount = ''
			# seasoncount = seasons.Seasons.seasonCountParse(season=season, items=result)

			# poster = client.parseDOM(item2, 'poster')
			# poster = '%s%s' % (imageUrl, poster[0]) if poster else ''

			# season_poster = [x for x in artwork if client.parseDOM(x, 'Season')[0] == season]
			# season_poster = client.parseDOM(season_poster[0], 'BannerPath')
			# season_poster = '%s%s' % (imageUrl, season_poster[0]) if season_poster else ''
			# season_poster = client.replaceHTMLCodes(season_poster)

			# banner = client.parseDOM(item2, 'banner')
			# banner = '%s%s' % (imageUrl, banner[0]) if banner else ''

			# fanart = client.parseDOM(item2, 'fanart')
			# fanart = '%s%s' % (imageUrl, fanart[0]) if fanart else ''

			# thumb = client.parseDOM(item, 'filename')
			# thumb = '%s%s' % (imageUrl, thumb[0]) if thumb else ''

			# if poster: pass
			# elif fanart != '': poster = fanart
			# elif banner != '': poster = banner

			# if banner: pass
			# elif fanart != '': banner = fanart
			# elif poster != '': banner = poster

			# if thumb: pass
			# elif fanart != '': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
			# elif poster != '': thumb = poster

			# studio = i['studio'] or client.parseDOM(item2, 'Network')[0]

			# genre = client.parseDOM(item2, 'Genre')[0]
			# genre = [x for x in genre.split('|') if x != '']
			# genre = ' / '.join(genre)

			# duration = client.parseDOM(item2, 'Runtime')[0] or ''
			# rating = client.parseDOM(item, 'Rating')[0]
			# votes = client.parseDOM(item2, 'RatingCount')[0]
			# mpaa = client.parseDOM(item2, 'ContentRating')[0]

			# director = client.replaceHTMLCodes(client.parseDOM(item, 'Director')[0])
			# director = ' / '.join([x for x in director.split('|') if x != ''])
			# writer = client.replaceHTMLCodes(client.parseDOM(item, 'Writer')[0]) 
			# writer = ' / '.join([x for x in writer.split('|') if x != ''])

			## castandart = parseActors(actors) or []
			# castandart = cache.get(parseActors, 96, actors) or []

			# plot = client.parseDOM(item, 'Overview')[0]
			# if not plot: plot = client.parseDOM(item2, 'Overview')[0]
			# plot = client.replaceHTMLCodes(plot)

			# values = {'title': title, 'total_seasons': total_seasons, 'total_episodes': total_episodes, 'seasoncount': seasoncount, 'season': season, 'episode': episode,
							# 'year': year, 'tvshowtitle': tvshowtitle, 'premiered': premiered, 'added': added, 'lastplayed': lastplayed, 'status': status,
							# 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer,
							# 'castandart': castandart, 'plot': plot, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': poster, 'season_poster': season_poster,  'banner': banner,
							# 'fanart': fanart, 'thumb': thumb, 'unaired': unaired, 'trailer': trailer, 'episodeIDS': episodeIDS, 'traktProgress': True} # idt snum and enum are needed anymore at this point
			# if not direct: values['action'] = 'episodes'

			# if 'airday' in i and i['airday'] is not None and i['airday'] != '':
				# values['airday'] = i['airday']
			# if 'airtime' in i and i['airtime'] is not None and i['airtime'] != '':
				# values['airtime'] = i['airtime']
			# if 'airzone' in i and i['airzone'] is not None and i['airzone'] != '':
				# values['airzone'] = i['airzone']
			# self.list.append(values)
		# except:
			# log_utils.error()

	# items = items[:len(items)]
	# threads = []
	# for i in items:
		# threads.append(workers.Thread(items_list, i))
	# [i.start() for i in threads]
	# [i.join() for i in threads]
	# return self.list