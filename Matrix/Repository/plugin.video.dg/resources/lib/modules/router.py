# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from urllib.parse import quote_plus
from resources.lib.modules import control

def router(params):
	action = params.get('action')
	id = params.get('id')
	name = params.get('name')
	title = params.get('title')
	tvshowtitle = params.get('tvshowtitle')
	year = params.get('year')
	imdb = params.get('imdb')
	tmdb = params.get('tmdb')
	tvdb = params.get('tvdb')
	season = params.get('season')
	episode = params.get('episode')
	type = params.get('type')
	url = params.get('url')
	query = params.get('query')
	source = params.get('source')

	if action is None:
		from resources.lib.menus import navigator
		isUpdate = control.homeWindow.getProperty('dg.updated')
		if isUpdate == 'true':
			control.execute('RunPlugin(plugin://plugin.video.dg/?action=tools_cleanSettings)')
			control.homeWindow.clearProperty('dg.updated')
			from resources.lib.modules import changelog
			changelog.get('DG')
		navigator.Navigator().root()

	####################################################
	#---MOVIES
	####################################################
	# elif action and action.startswith('movies_'):
	elif action == 'movieNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().movies()
	elif action == 'movieliteNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().movies(lite=True)
	elif action == 'mymovieNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().mymovies()
	elif action == 'mymovieliteNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().mymovies(lite=True)
	elif action == 'movies':
		from resources.lib.menus import movies
		movies.Movies().get(url)
	elif action == 'moviePage':
		from resources.lib.menus import movies
		movies.Movies().get(url)
	elif action == 'tmdbmovies':
		from resources.lib.menus import movies
		movies.Movies().getTMDb(url)
	elif action == 'tmdbmoviePage':
		from resources.lib.menus import movies
		movies.Movies().getTMDb(url)
	elif action == 'movieSearch':
		from resources.lib.menus import movies
		movies.Movies().search()
	elif action == 'movieSearchnew':
		from resources.lib.menus import movies
		movies.Movies().search_new()
	elif action == 'movieSearchterm':
		from resources.lib.menus import movies
		movies.Movies().search_term(name)
	elif action == 'moviePerson':
		from resources.lib.menus import movies
		movies.Movies().person()
	elif action == 'movieGenres':
		from resources.lib.menus import movies
		movies.Movies().genres(url)
	elif action == 'movieLanguages':
		from resources.lib.menus import movies
		movies.Movies().languages()
	elif action == 'movieCertificates':
		from resources.lib.menus import movies
		movies.Movies().certifications(url)
	elif action == 'movieYears':
		from resources.lib.menus import movies
		movies.Movies().years(url)
	elif action == 'moviePersons':
		from resources.lib.menus import movies
		movies.Movies().persons(url)
	elif action == 'moviesUnfinished':
		from resources.lib.menus import movies
		movies.Movies().unfinished(url)
	elif action == 'movieUserlists':
		from resources.lib.menus import movies
		movies.Movies().userlists()
	elif action == 'movies_PublicLists':
		from resources.lib.menus import movies
		movies.Movies().getTraktPublicLists(url)
	elif action == 'movies_SearchLists':
		from resources.lib.menus import navigator
		media_type = params.get('media_type')
		navigator.Navigator().traktSearchLists(media_type)
	elif action == 'movies_LikedLists':
		from resources.lib.menus import movies
		movies.Movies().traktLlikedlists()
	elif action == 'movies_traktUnfinishedManager':
		from resources.lib.menus import movies
		movies.Movies().unfinishedManager()
	elif action == 'movies_traktCollectionManager':
		from resources.lib.menus import movies
		movies.Movies().collectionManager()
	elif action == 'movies_traktWatchListManager':
		from resources.lib.menus import movies
		movies.Movies().watchlistManager()

	####################################################
	#---Collections
	####################################################
	elif action and action.startswith('collections'):
		if action == 'collections_Navigator':
			from resources.lib.menus import collections
			collections.Collections().collections_Navigator()
		elif action == 'collections_Boxset':
			from resources.lib.menus import collections
			collections.Collections().collections_Boxset()
		elif action == 'collections_Kids':
			from resources.lib.menus import collections
			collections.Collections().collections_Kids()
		elif action == 'collections_BoxsetKids':
			from resources.lib.menus import collections
			collections.Collections().collections_BoxsetKids()
		elif action == 'collections_Superhero':
			from resources.lib.menus import collections
			collections.Collections().collections_Superhero()
		elif action == 'collections_MartialArts':
			from resources.lib.menus import collections
			collections.Collections().collections_martial_arts()
		elif action == 'collections_MartialArtsActors':
			from resources.lib.menus import collections
			collections.Collections().collections_martial_arts_actors()
		elif action == 'collections':
			from resources.lib.menus import collections
			collections.Collections().get(url)

	####################################################
	# TV Shows
	####################################################
	# if action and action.startswith('tv_'):
	elif action == 'tvNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().tvshows()

	elif action == 'tvliteNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().tvshows(lite=True)

	elif action == 'mytvNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().mytvshows()

	elif action == 'mytvliteNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().mytvshows(lite=True)

	elif action == 'tvshows':
		from resources.lib.menus import tvshows
		tvshows.TVshows().get(url)

	elif action == 'tvshowPage':
		from resources.lib.menus import tvshows
		tvshows.TVshows().get(url)

	elif action == 'tmdbTvshows':
		from resources.lib.menus import tvshows
		tvshows.TVshows().getTMDb(url)

	elif action == 'tmdbTvshowPage':
		from resources.lib.menus import tvshows
		tvshows.TVshows().getTMDb(url)

	elif action == 'tvmazeTvshows':
		from resources.lib.menus import tvshows
		tvshows.TVshows().getTVmaze(url)

	elif action == 'tvmazeTvshowPage':
		from resources.lib.menus import tvshows
		tvshows.TVshows().getTVmaze(url)

	elif action == 'tvSearch':
		from resources.lib.menus import tvshows
		tvshows.TVshows().search()

	elif action == 'tvSearchnew':
		from resources.lib.menus import tvshows
		tvshows.TVshows().search_new()

	elif action == 'tvSearchterm':
		from resources.lib.menus import tvshows
		tvshows.TVshows().search_term(name)

	elif action == 'tvPerson':
		from resources.lib.menus import tvshows
		tvshows.TVshows().person()

	elif action == 'tvGenres':
		from resources.lib.menus import tvshows
		tvshows.TVshows().genres(url)

	elif action == 'tvNetworks':
		from resources.lib.menus import tvshows
		tvshows.TVshows().networks()

	elif action == 'tvLanguages':
		from resources.lib.menus import tvshows
		tvshows.TVshows().languages()

	elif action == 'tvCertificates':
		from resources.lib.menus import tvshows
		tvshows.TVshows().certifications()

	elif action == 'tvYears':
		from resources.lib.menus import tvshows
		tvshows.TVshows().years(url)

	elif action == 'tvPersons':
		from resources.lib.menus import tvshows
		tvshows.TVshows().persons(url)

	elif action == 'tvUserlists':
		from resources.lib.menus import tvshows
		tvshows.TVshows().userlists()

	elif action == 'tvOriginals':
		from resources.lib.menus import tvshows
		tvshows.TVshows().originals()

	elif action == 'tv_PublicLists':
		from resources.lib.menus import tvshows
		tvshows.TVshows().getTraktPublicLists(url)

	elif action == 'tv_SearchLists':
		from resources.lib.menus import navigator
		media_type = params.get('media_type')
		navigator.Navigator().traktSearchLists(media_type)

	elif action == 'shows_LikedLists':
		from resources.lib.menus import tvshows
		tvshows.TVshows().traktLlikedlists()

	elif action == 'shows_traktHiddenManager':
		from resources.lib.menus import tvshows
		tvshows.TVshows().traktHiddenManager()

	elif action == 'shows_traktCollectionManager':
		from resources.lib.menus import tvshows
		tvshows.TVshows().collectionManager()

	elif action == 'shows_traktWatchListManager':
		from resources.lib.menus import tvshows
		tvshows.TVshows().watchlistManager()

	####################################################
	#---SEASONS
	####################################################
	elif action == 'seasons':
		from resources.lib.menus import seasons
		art = params.get('art')
		seasons.Seasons().get(tvshowtitle, year, imdb, tmdb, tvdb, art)

	####################################################
	#---EPISODES
	####################################################
	elif action == 'episodes':
		from resources.lib.menus import episodes
		meta = params.get('meta')
		episodes.Episodes().get(tvshowtitle, year, imdb, tmdb, tvdb, meta, season, episode)

	elif action == 'calendar':
		from resources.lib.menus import episodes
		episodes.Episodes().calendar(url)

	elif action == 'upcomingProgress':
		from resources.lib.menus import episodes
		episodes.Episodes().upcoming_progress(url)

	elif action == 'episodes_clrProgressCache':
		from resources.lib.menus import episodes
		episodes.Episodes().clr_progress_cache(url)

	elif action == 'calendars':
		from resources.lib.menus import episodes
		episodes.Episodes().calendars()

	elif action == 'episodesUnfinished':
		from resources.lib.menus import episodes
		episodes.Episodes().unfinished(url)

	elif action == 'episodes_traktUnfinishedManager':
		from resources.lib.menus import episodes
		episodes.Episodes().unfinishedManager()

	####################################################
	#---Premium Services
	####################################################
	elif action == 'premiumNavigator':
		from resources.lib.menus import navigator
		navigator.Navigator().premium_services()

	elif action and action.startswith('ad_'):
		if action == 'ad_ServiceNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().alldebrid_service()
		elif action == 'ad_AccountInfo':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().account_info_to_dialog()
		# elif action == 'ad_Authorize':
			# from resources.lib.debrid import alldebrid
			# alldebrid.AllDebrid().auth()
		elif action == 'ad_Transfers':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().user_transfers_to_listItem()
		elif action == 'ad_CloudStorage':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().user_cloud_to_listItem()
		elif action == 'ad_BrowseUserCloud':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().browse_user_cloud(source)
		elif action == 'ad_DeleteTransfer':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().delete_transfer(id, name, silent=False)
		elif action == 'ad_RestartTransfer':
			from resources.lib.debrid import alldebrid
			alldebrid.AllDebrid().restart_transfer(id, name, silent=False)

	elif action and action.startswith('en_'):
		if action == 'en_ServiceNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().easynews_service()
		elif action == 'en_Search':
			from resources.lib.debrid import easynews
			easynews.EasyNews().search()
		elif action == 'en_Searchnew':
			from resources.lib.debrid import easynews
			easynews.EasyNews().search_new()
		elif action == 'en_searchResults':
			from resources.lib.debrid import easynews
			easynews.EasyNews().query_results_to_dialog(query)
		elif action == 'en_resolve_forPlayback':
			from resources.lib.debrid import easynews
			easynews.EasyNews().resolve_forPlayback(url)
		elif action == 'en_AccountInfo':
			from resources.lib.debrid import easynews
			easynews.EasyNews().account_info_to_dialog()

	elif action and action.startswith('furk_'):
		if action == "furk_ServiceNavigator":
			from resources.lib.menus import navigator
			navigator.Navigator().furk_service()
		elif action == "furk_Search":
			from resources.lib.debrid import furk
			furk.Furk().search()
		elif action == "furk_SearchNew":
			from resources.lib.debrid import furk
			furk.Furk().search_new()
		elif action == "furk_searchResults":
			from resources.lib.debrid import furk
			furk.Furk().query_results_to_dialog(query)
		elif action == 'furk_resolve_forPlayback':
			from resources.lib.debrid import furk
			furk.Furk().resolve_forPlayback(url)
		elif action == 'furk_AccountInfo':
			from resources.lib.debrid import furk
			furk.Furk().account_info_to_dialog()
		elif action == "furk_UserFiles":
			from resources.lib.debrid import furk
			furk.Furk().user_files()

	elif action and action.startswith('pm_'):
		if action == 'pm_ServiceNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().premiumize_service()
		elif action == 'pm_AccountInfo':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().account_info_to_dialog()
		# elif action == 'pm_Authorize':
			# from resources.lib.debrid import premiumize
			# premiumize.Premiumize().auth()
		elif action == 'pm_MyFiles':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().my_files_to_listItem(id, name)
		elif action == 'pm_Transfers':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().user_transfers_to_listItem()
		elif action == 'pm_Rename':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().rename(type, id, name)
		elif action == 'pm_Delete':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().delete(type, id, name)
		elif action == 'pm_DeleteTransfer':
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().delete_transfer(id, name)
		elif action == 'pm_ClearFinishedTransfers': # disabled for now till PM fixes
			from resources.lib.debrid import premiumize
			premiumize.Premiumize().clear_finished_transfers()

	elif action and action.startswith('rd_'):
		if action == 'rd_ServiceNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().realdebrid_service()
		elif action == 'rd_AccountInfo':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().account_info_to_dialog()
		# elif action == 'rd_Authorize':
			# from resources.lib.debrid import realdebrid
			# realdebrid.RealDebrid().auth()
		elif action == 'rd_UserTorrentsToListItem':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().user_torrents_to_listItem()
		elif action == 'rd_MyDownloads':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().my_downloads_to_listItem(int(query))
		elif action == 'rd_BrowseUserTorrents':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().browse_user_torrents(id)
		elif action == 'rd_DeleteUserTorrent':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().delete_user_torrent(id, name)
		elif action == 'rd_DeleteDownload':
			from resources.lib.debrid import realdebrid
			realdebrid.RealDebrid().delete_download(id, name)

	####################################################
	#---Anime
	####################################################
	elif action and action.startswith('anime_'):
		if action == 'anime_Navigator':
			from resources.lib.menus import navigator
			navigator.Navigator().anime()
		elif action == 'anime_Movies':
			from resources.lib.menus import movies
			movies.Movies().get(url)
		elif action == 'anime_TVshows':
			from resources.lib.menus import tvshows
			tvshows.TVshows().get(url)

	####################################################
	#---YouTube
	####################################################
	elif action == 'youtube':
		from resources.lib.menus import youtube
		if id is None: youtube.yt_index().root(action)
		else: youtube.yt_index().get(action, id)

	elif action == 'sectionItem':
		pass # Placeholder. This is a non-clickable menu item for notes, etc.

	####################################################
	#---Download
	####################################################
	elif action and action.startswith('download'):
		if action == 'downloadNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().downloads()
		elif action == 'download':
			caller = params.get('caller')
			image = params.get('image')
			if caller == 'sources': # future, move to downloader module for pack support
				control.busy()
				try:
					from json import loads as jsloads
					from resources.lib.modules import sources
					from resources.lib.modules import downloader
					downloader.download(name, image, sources.Sources().sourcesResolve(jsloads(source)[0]), title)
				except:
					import traceback
					traceback.print_exc()
			if caller == 'alldebrid':
				control.busy()
				try:
					from resources.lib.modules import downloader
					from resources.lib.debrid import alldebrid
					downloader.download(name, image, alldebrid.AllDebrid().unrestrict_link(url.replace(' ', '%20')))
				except:
					import traceback
					traceback.print_exc()
			if caller == 'easynews':
				control.busy()
				try:
					from resources.lib.modules import downloader
					downloader.download(name, image, url)
				except:
					import traceback
					traceback.print_exc()
			if caller == 'premiumize':
				control.busy()
				try:
					from resources.lib.modules import downloader
					from resources.lib.debrid import premiumize
					downloader.download(name, image, premiumize.Premiumize().add_headers_to_url(url.replace(' ', '%20')))
				except:
					import traceback
					traceback.print_exc()
			if caller == 'realdebrid':
				control.busy()
				try:
					from resources.lib.modules import downloader
					from resources.lib.debrid import realdebrid
					if type == 'unrestrict':
						downloader.download(name, image, realdebrid.RealDebrid().unrestrict_link(url.replace(' ', '%20')))
					else:
						downloader.download(name, image, url.replace(' ', '%20'))
				except:
					import traceback
					traceback.print_exc()


	####################################################
	#---Tools
	####################################################
	elif action and action.startswith('tools_'):
		if action == 'tools_ShowNews':
			from resources.lib.modules import newsinfo
			newsinfo.news()
		elif action == 'tools_ShowChangelog':
			from resources.lib.modules import changelog
			changelog.get(name)
		elif action == 'tools_ShowHelp':
			from resources.help import help
			help.get(name)
		elif action == 'tools_LanguageInvoker':
			from resources.lib.modules import language_invoker
			language_invoker.set_reuselanguageinvoker()
		elif action == 'tools_toolNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().tools()
		elif action == 'tools_traktToolsNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().traktTools()
		elif action == 'tools_searchNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().search()
		elif action == 'tools_viewsNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().views()
		elif action == 'tools_loggingNavigator':
			from resources.lib.menus import navigator
			navigator.Navigator().loggingNavigator()
		elif action == 'tools_addView':
			from resources.lib.modules import views
			content = params.get('content')
			views.addView(content)
		elif action == 'tools_resetViewTypes':
			from resources.lib.modules import views
			views.clearViews()
		elif action == 'tools_cleanSettings':
			from resources.lib.modules import clean_settings
			clean_settings.clean_settings()
		elif action == 'tools_openMyAccount':
			from myaccounts import openMASettings
			from resources.lib.modules import my_accounts
			openMASettings(query)
			control.sleep(500)
			while control.condVisibility('Window.IsVisible(addonsettings)') or control.homeWindow.getProperty('myaccounts.active') == 'true':
				control.sleep(500)
			control.sleep(100)
			my_accounts.syncMyAccounts()
			control.sleep(100)
			if params.get('opensettings') == 'true':
				control.openSettings(params.get('query2'), 'plugin.video.dg')
		elif action == 'tools_syncMyAccount':
			from resources.lib.modules import my_accounts
			my_accounts.syncMyAccounts()
			if params.get('opensettings') == 'true':
				control.openSettings(query, 'plugin.video.dg')
		elif action == 'tools_traktAcctMyAccounts':
			control.execute('RunScript(script.module.myaccounts, action=traktAcct)')
		elif action == 'tools_adAcctMyAccounts':
			control.execute('RunScript(script.module.myaccounts, action=alldebridAcct)')
		elif action == 'tools_pmAcctMyAccounts':
			control.execute('RunScript(script.module.myaccounts, action=premiumizeAcct)')
		elif action == 'tools_rdAcctMyAccounts':
			control.execute('RunScript(script.module.myaccounts, action=realdebridAcct)')
		elif action == 'tools_openSettings':
			control.openSettings(query)
		elif action == 'tools_contextDGSettings':
			control.openSettings('0.0', 'context.dg')
			control.trigger_widget_refresh()
		elif action == 'tools_fenomscrapersSettings':
			control.openSettings('0.0', 'script.module.fenomscrapers')
		elif action == 'tools_traktManager':
			from resources.lib.modules import trakt
			watched = (params.get('watched') == 'True') if params.get('watched') else None
			unfinished = (params.get('unfinished') == 'True') if params.get('unfinished') else False
			trakt.manager(name, imdb, tvdb, season, episode, watched=watched, unfinished=unfinished)
		elif action == 'tools_likeList':
			from resources.lib.modules import trakt
			trakt.like_list(params.get('list_owner'), params.get('list_name'), params.get('list_id'))
		elif action == 'tools_unlikeList':
			from resources.lib.modules import trakt
			trakt.unlike_list(params.get('list_owner'), params.get('list_name'), params.get('list_id'))
		elif action == 'tools_forceTraktSync':
			from resources.lib.modules import trakt
			trakt.force_traktSync()
		elif action == 'tools_clearLogFile':
			from resources.lib.modules import log_utils
			cleared = log_utils.clear_logFile()
			if cleared == 'canceled': return
			elif cleared: control.notification(message='DG Log File Successfully Cleared')
			else: control.notification(message='Error clearing DG Log File, see kodi.log for more info')
		elif action == 'tools_viewLogFile':
			from resources.lib.modules import log_utils
			log_utils.view_LogFile(name)
		elif action == 'tools_uploadLogFile':
			from resources.lib.modules import log_utils
			log_utils.upload_LogFile(name)
		elif action == 'tools_traktLikedListManager':
			from resources.lib.menus import movies
			movies.Movies().likedListsManager()

	####################################################
	#---Service
	####################################################
	elif action and action.startswith('service_'):
		if action == 'service_syncTrakt':
			from resources.lib.modules import trakt
			trakt.trakt_service_sync()
		elif action == 'service_library':
			from resources.lib.modules import library
			library.lib_tools().service()

	####################################################
	#---Play
	####################################################
	elif action and action.startswith('play_'):
		if action == 'play_Item':
			from resources.lib.modules import sources
			premiered = params.get('premiered')
			meta = params.get('meta')
			select = params.get('select')
			rescrape = params.get('rescrape')
			# custom_query = params.get('custom_query')
			all_providers = params.get('all_providers')
			sources.Sources(all_providers).play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select, rescrape)

		elif action == "play_preScrapeNext":
			from resources.lib.modules.player import PlayNext
			PlayNext().prescrapeNext()

		elif action == "play_nextWindowXML":
			from resources.lib.modules.player import PlayNext
			play_next = PlayNext()
			play_next.display_xml()
			del play_next

		elif action == 'play_All': # context menu works same as "Play from Here"
			control.player2().play(control.playlist) 

		elif action == 'play_URL':
			caller = params.get('caller')
			if caller == 'realdebrid':
				from resources.lib.debrid import realdebrid
				if type == 'unrestrict': control.player.play(realdebrid.RealDebrid().unrestrict_link(url.replace(' ', '%20')))
				else: control.player.play(url.replace(' ', '%20'))
			elif caller == 'alldebrid':
				from resources.lib.debrid import alldebrid
				if type == 'unrestrict': control.player.play(alldebrid.AllDebrid().unrestrict_link(url.replace(' ', '%20')))
				else: control.player.play(url.replace(' ', '%20'))
			else: control.player.play(url.replace(' ', '%20'))

		elif action == 'play_EpisodesList': # global context option
			from json import dumps as jsdumps
			from resources.lib.menus import episodes
			meta = params.get('meta')
			items = episodes.Episodes().get(tvshowtitle, year, imdb, tmdb, tvdb, meta, season, episode, create_directory=False)
			control.playlist.clear()
			for i in items:
				title = i['title']
				systitle = quote_plus(title)
				year = i['year']
				imdb = i['imdb']
				tmdb = i['tmdb']
				tvdb = i['tvdb']
				season = i['season']
				episode = i['episode']
				tvshowtitle = i['tvshowtitle']
				systvshowtitle = quote_plus(tvshowtitle)
				premiered = i['premiered']
				sysmeta = quote_plus(jsdumps(i))
				url = 'plugin://plugin.video.dg/?action=play_Item&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&select=1' % (
										systitle, year, imdb, tmdb, tvdb, season, episode, systvshowtitle, premiered, sysmeta)
				item = control.item(label=title, offscreen=True)
				control.playlist.add(url=url, listitem=item)
			control.player2().play(control.playlist)

		elif action == 'play_Trailer':
			from resources.lib.modules import trailer
			windowedtrailer = params.get('windowedtrailer')
			windowedtrailer = int(windowedtrailer) if windowedtrailer in ("0","1") else 0
			trailer.Trailer().play(type, name, year, url, imdb, windowedtrailer)

		elif action == 'play_Random':
			rtype = params.get('rtype')
			if rtype == 'movie':
				from resources.lib.menus import movies
				rlist = movies.Movies().get(url, create_directory=False)
				r = 'plugin://plugin.video.dg/?action=play_Item'
			elif rtype == 'episode':
				from resources.lib.menus import episodes
				meta = params.get('meta')
				rlist = episodes.Episodes().get(tvshowtitle, year, imdb, tmdb, tvdb, meta, season, create_directory=False)
				r = 'plugin://plugin.video.dg/?action=play_Item'
			elif rtype == 'season':
				from resources.lib.menus import seasons
				art = params.get('art')
				rlist = seasons.Seasons().get(tvshowtitle, year, imdb, tmdb, tvdb, art, create_directory=False)
				r = 'plugin://plugin.video.dg/?action=play_Random&rtype=episode'
			elif rtype == 'show':
				from resources.lib.menus import tvshows
				rlist = tvshows.TVshows().get(url, create_directory=False)
				r = 'plugin://plugin.video.dg/?action=play_Random&rtype=season'
			from random import randint
			from json import dumps as jsdumps
			try:
				rand = randint(1,len(rlist))-1
				for p in ('title', 'year', 'imdb', 'tmdb', 'tvdb', 'season', 'episode', 'tvshowtitle', 'premiered', 'select'):
					if rtype == "show" and p == "tvshowtitle":
						try: r += '&' + p + '=' + quote_plus(rlist[rand]['title'])
						except: pass
					else:
						try: r += '&' + p + '=' + quote_plus(str(rlist[rand][p]))
						except: pass
				try: r += '&meta=' + quote_plus(jsdumps(rlist[rand]))
				except: r += '&meta=' + quote_plus("{}")
				if rtype == "movie":
					try: control.notification(title=32536, message='%s (%s)' % (rlist[rand]['title'], rlist[rand]['year']))
					except: pass
				elif rtype == "episode":
					try: control.notification(title=32536, message='%s - %01dx%02d - %s' % (rlist[rand]['tvshowtitle'], int(rlist[rand]['season']), int(rlist[rand]['episode']), rlist[rand]['title']))
					except: pass
				control.execute('RunPlugin(%s)' % r)
			except:
				control.notification(message=32537)

	elif action == 'play': # for support of old style .strm library files
		from resources.lib.modules import sources
		premiered = params.get('premiered')
		meta = params.get('meta')
		select = params.get('select')
		rescrape = params.get('rescrape')
		all_providers = params.get('all_providers')
		sources.Sources(all_providers).play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select, rescrape)

	####################################################
	#---Playlist
	####################################################
	elif action and action.startswith('playlist_'):
		if action == 'playlist_Manager':
			from resources.lib.modules import playlist
			art = params.get('art')
			meta = params.get('meta')
			playlist.playlistManager(name, url, meta, art)
		elif action == 'playlist_Show':
			from resources.lib.modules import playlist
			playlist.playlistShow()
		elif action == 'playlist_Clear':
			from resources.lib.modules import playlist
			playlist.playlistClear()
		elif action == 'playlist_QueueItem':
			control.queueItem()
			if name is None: control.notification(title=35515, message=35519)
			else: control.notification(title=name, message=35519)

	####################################################
	#---Playcount
	####################################################
	elif action and action.startswith('playcount_'):
		if action == 'playcount_Movie':
			from resources.lib.modules import playcount
			playcount.movies(name, imdb, query)
		elif action == 'playcount_Episode':
			from resources.lib.modules import playcount
			playcount.episodes(name, imdb, tvdb, season, episode, query)
		elif action == 'playcount_TVShow':
			from resources.lib.modules import playcount
			playcount.tvshows(name, imdb, tvdb, season, query)

	####################################################
	#---Source Actions
	####################################################
	elif action == 'alterSources':
		from resources.lib.modules import sources
		meta = params.get('meta')
		sources.Sources().alterSources(url, meta)

	elif action == 'showDebridPack':
		from resources.lib.modules.sources import Sources
		caller = params.get('caller')
		Sources().debridPackDialog(caller, name, url, source)

	elif action == 'sourceInfo':
		from resources.lib.modules.sources import Sources
		Sources().sourceInfo(source)

	elif action == 'cacheTorrent':
		caller = params.get('caller')
		pack = True if type == 'pack' else False
		if caller == 'RD':
			from resources.lib.debrid.realdebrid import RealDebrid as debrid_function
		elif caller == 'PM':
			from resources.lib.debrid.premiumize import Premiumize as debrid_function
		elif caller == 'AD':
			from resources.lib.debrid.alldebrid import AllDebrid as debrid_function
		success = debrid_function().add_uncached_torrent(url, pack=pack)
		if success:
			from resources.lib.modules import sources
			meta = params.get('meta')
			items = params.get('items')
			sources.Sources().playItem(title, items, source, meta)

	elif action == 'rescrapeMenu':
		from resources.lib.modules import sources
		premiered = params.get('premiered')
		meta = params.get('meta')
		highlight_color = control.getHighlightColor()
		items = [control.lang(32207), control.lang(32208), control.lang(32209) % highlight_color, control.lang(32210) % highlight_color, control.lang(32216) % highlight_color, control.lang(32217) % highlight_color]
		select = control.selectDialog(items, heading=control.addonInfo('name') + ' - ' + 'Rescrape Options Menu')
		if select == -1: return control.closeAll()
		if select >= 0:
			if select == 0: sources.Sources().play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='1', rescrape='true')
			elif select == 1: sources.Sources().play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='0', rescrape='true')
			elif select == 2: sources.Sources(all_providers='true').play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='1', rescrape='true')
			elif select == 3: sources.Sources(all_providers='true').play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='0', rescrape='true')
			elif select == 4: sources.Sources(custom_query='true').play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='0', rescrape='true')
			elif select == 5: sources.Sources(all_providers='true', custom_query='true').play(title, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select='0', rescrape='true')

	####################################################
	#---Library Actions
	####################################################
	elif action and action.startswith('library_'):
		if action == 'library_Navigator':
			from resources.lib.menus import navigator
			navigator.Navigator().library()
		elif action == 'library_movieToLibrary':
			from resources.lib.modules import library
			library.libmovies().add(name, title, year, imdb, tmdb)
		elif action == 'library_moviesToLibrary':
			from resources.lib.modules import library
			library.libmovies().range(url, name)
		elif action == 'library_moviesListToLibrary':
			from resources.lib.menus import movies
			movies.Movies().moviesListToLibrary(url)
		elif action == 'library_moviesToLibrarySilent':
			from resources.lib.modules import library
			library.libmovies().silent(url)
		elif action == 'library_tvshowToLibrary':
			from resources.lib.modules import library
			library.libtvshows().add(tvshowtitle, year, imdb, tmdb, tvdb)
		elif action == 'library_tvshowsToLibrary':
			from resources.lib.modules import library
			library.libtvshows().range(url, name)
		elif action == 'library_tvshowsListToLibrary':
			from resources.lib.menus import tvshows
			tvshows.TVshows().tvshowsListToLibrary(url)
		elif action == 'library_tvshowsToLibrarySilent':
			from resources.lib.modules import library
			library.libtvshows().silent(url)
		elif action == 'library_update':
			control.notification(message=32085)
			from resources.lib.modules import library
			library.libepisodes().update()
			library.libmovies().list_update()
			library.libtvshows().list_update()
			while True:
				if control.condVisibility('Library.IsScanningVideo'):
					control.sleep(3000)
					continue
				else: break
			control.sleep(1000)
			control.notification(message=32086)
		elif action == 'library_clean':
			from resources.lib.modules import library
			library.lib_tools().clean()
		elif action == 'library_setup':
			from resources.lib.modules import library
			library.lib_tools().total_setup()

	####################################################
	#---Cache
	####################################################
	elif action and action.startswith('cache_'):
		if action == 'cache_Navigator':
			from resources.lib.menus import navigator
			navigator.Navigator().cf()
		elif action == 'cache_clearAll':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCacheAll()
		elif action == 'cache_clearSources':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCacheProviders()
		elif action == 'cache_clearMeta':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCacheMeta()
		elif action == 'cache_clearCache':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCache()
		elif action == 'cache_clearMetaAndCache':
			from resources.lib.menus import navigator
			navigator.Navigator().clearMetaAndCache()
		elif action == 'cache_clearSearch':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCacheSearch() 
		elif action == 'cache_clearSearchPhrase':
			from resources.lib.menus import navigator
			navigator.Navigator().clearCacheSearchPhrase(source, name)
		elif action == 'cache_clearBookmarks':
			from resources.lib.menus import navigator
			navigator.Navigator().clearBookmarks()
		elif action == 'cache_clearBookmark':
			from resources.lib.menus import navigator
			navigator.Navigator().clearBookmark(name, year)
		elif action == 'cache_clearKodiBookmark': # context.dg action call only
			from resources.lib.database import cache
			cache.clear_local_bookmark(url)