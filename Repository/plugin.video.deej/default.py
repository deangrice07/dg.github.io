# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: MuadDib

# respect for the original developer MuadDib

# New fixed #
# Addon Name: Deej
# Addon id: plugin.video.deej
# Addon Provider: Grice Advice

import urlparse,sys,urllib
from resources.lib.modules import control
from resources.lib.modules import log_utils


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
mode = params.get('mode')
subid = params.get('subid')
name = params.get('name')
title = params.get('title')
year = params.get('year')
imdb = params.get('imdb')
tvdb = params.get('tvdb')
tmdb = params.get('tmdb')
season = params.get('season')
episode = params.get('episode')
tvshowtitle = params.get('tvshowtitle')
premiered = params.get('premiered')
docu_category = params.get('docuCat')
docu_watch = params.get('docuPlay')
url = params.get('url')
image = params.get('image')
meta = params.get('meta')
select = params.get('select')
query = params.get('query')
source = params.get('source')
content = params.get('content')
folder = params.get('folder')
poster = params.get('poster')
setting = params.get('setting')
windowedtrailer = params.get('windowedtrailer')


if action == None:
    from resources.lib.indexers import navigator
    from resources.lib.modules import cache
    cache.cache_version_check()
    navigator.navigator().root()

elif action == 'newsNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().news()

elif action == 'movieNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().movies()

elif action == 'movieliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().movies(lite=True)

elif action == 'mymovieNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mymovies()

elif action == 'mymovieliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mymovies(lite=True)

elif action == 'tvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshows()

elif action == 'tvliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshows(lite=True)

elif action == 'mytvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mytvshows()

elif action == 'mytvliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mytvshows(lite=True)

elif action == 'docuNavigator':
    from resources.lib.indexers import docu
    docu.documentary().root()

elif action == 'docuHeaven':
    from resources.lib.indexers import docu
    if not docu_category == None:
        docu.documentary().docu_list(docu_category)
    elif not docu_watch == None:
        docu.documentary().docu_play(docu_watch)
    else:
        docu.documentary().root()

elif action == 'downloadNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().downloads()

elif action == 'libraryNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().library()

elif action == 'toolNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tools()

elif action == 'searchNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().search()

elif action == 'viewsNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().views()

elif action == 'clearCache':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCache()

elif action == 'clearCacheSearch':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCacheSearch()

elif action == 'clearAllCache':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCacheAll()

elif action == 'clearMetaCache':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCacheMeta()
    
elif action == 'infoCheck':
    from resources.lib.indexers import navigator
    navigator.navigator().infoCheck('')

elif action == 'movies':
    from resources.lib.indexers import movies
    movies.movies().get(url)

elif action == 'moviePage':
    from resources.lib.indexers import movies
    movies.movies().get(url)

elif action == 'movieWidget':
    from resources.lib.indexers import movies
    movies.movies().widget()

elif action == 'movieSearch':
    from resources.lib.indexers import movies
    movies.movies().search()

elif action == 'movieSearchnew':
    from resources.lib.indexers import movies
    movies.movies().search_new()

elif action == 'movieSearchterm':
    from resources.lib.indexers import movies
    movies.movies().search_term(name)

elif action == 'moviePerson':
    from resources.lib.indexers import movies
    movies.movies().person()

elif action == 'movieGenres':
    from resources.lib.indexers import movies
    movies.movies().genres()

elif action == 'movieLanguages':
    from resources.lib.indexers import movies
    movies.movies().languages()

elif action == 'movieCertificates':
    from resources.lib.indexers import movies
    movies.movies().certifications()

elif action == 'movieYears':
    from resources.lib.indexers import movies
    movies.movies().years()

elif action == 'moviePersons':
    from resources.lib.indexers import movies
    movies.movies().persons(url)

elif action == 'movieUserlists':
    from resources.lib.indexers import movies
    movies.movies().userlists()

elif action == 'channels':
    from resources.lib.indexers import channels
    channels.channels().get()

elif action == 'tvshows':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().get(url)

elif action == 'tvshowPage':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().get(url)

elif action == 'tvSearch':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().search()

elif action == 'tvSearchnew':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().search_new()

elif action == 'tvSearchterm':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().search_term(name)
    
elif action == 'tvPerson':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().person()

elif action == 'tvGenres':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().genres()

elif action == 'tvReviews':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'movieReviews':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'tvNetworks':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().networks()

elif action == 'tvLanguages':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().languages()

elif action == 'tvCertificates':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().certifications()

elif action == 'tvPersons':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().persons(url)

elif action == 'tvUserlists':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().userlists()

elif action == 'seasons':
    from resources.lib.indexers import episodes
    episodes.seasons().get(tvshowtitle, year, imdb, tvdb)

elif action == 'episodes':
    from resources.lib.indexers import episodes
    episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season, episode)

elif action == 'calendar':
    from resources.lib.indexers import episodes
    episodes.episodes().calendar(url)

elif action == 'tvWidget':
    from resources.lib.indexers import episodes
    episodes.episodes().widget()

elif action == 'calendars':
    from resources.lib.indexers import episodes
    episodes.episodes().calendars()

elif action == 'episodeUserlists':
    from resources.lib.indexers import episodes
    episodes.episodes().userlists()

elif action == 'refresh':
    from resources.lib.modules import control
    control.refresh()

elif action == 'queueItem':
    from resources.lib.modules import control
    control.queueItem()

elif action == 'openSettings':
    from resources.lib.modules import control
    control.openSettings(query)

elif action == 'artwork':
    from resources.lib.modules import control
    control.artwork()

elif action == 'addView':
    from resources.lib.modules import views
    views.addView(content)

elif action == 'moviePlaycount':
    from resources.lib.modules import playcount
    playcount.movies(imdb, query)

elif action == 'episodePlaycount':
    from resources.lib.modules import playcount
    playcount.episodes(imdb, tvdb, season, episode, query)

elif action == 'tvPlaycount':
    from resources.lib.modules import playcount
    playcount.tvshows(name, imdb, tvdb, season, query)

elif action == 'trailer':
    from resources.lib.modules import trailer
    trailer.trailer().play(name, url, windowedtrailer)

elif action == 'traktManager':
    from resources.lib.modules import trakt
    trakt.manager(name, imdb, tvdb, content)

elif action == 'authTrakt':
    from resources.lib.modules import trakt
    trakt.authTrakt()

elif action == 'urlResolver':
    try: import resolveurl
    except: pass
    resolveurl.display_settings()

elif action == 'download':
    import json
    from resources.lib.modules import sources
    from resources.lib.modules import downloader
    try: downloader.download(name, image, sources.sources().sourcesResolve(json.loads(source)[0], True))
    except: pass

elif action == 'kidscorner':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'fitness':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'legends':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'browser':
    from resources.lib.indexers import iptv
    iptv.resolver().browser(url)

elif action == 'lists_play':
    from resources.lib.indexers import iptv
    iptv.player().play(url, content)


elif action == 'smuSettings':
    try: import resolveurl
    except: pass
    resolveurl.display_settings()

elif action == 'alterSources':
    from resources.lib.modules import sources
    sources.sources().alterSources(url, meta)

elif action == 'installdeejscrapers':
    from resources.lib.modules import control
    control.installAddon('script.module.deejscrapers')
    control.sleep(200)
    control.refresh()

elif action == 'deejscrapersettings':
    from resources.lib.modules import control
    control.openSettings('0.0', 'script.module.deejscrapers')

elif action == 'openscrapersettings':
    from resources.lib.modules import control
    control.openSettings('0.0', 'script.module.openscrapers')

elif action == 'sectionItem':
    pass # Placeholder. This is a non-clickable menu item for notes, etc.

elif action == 'play':
    from resources.lib.modules import sources
    sources.sources().play(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, select)

elif action == 'addItem':
    from resources.lib.modules import sources
    sources.sources().addItem(title)

elif action == 'playItem':
    from resources.lib.modules import sources
    sources.sources().playItem(title, source)

elif action == 'alterSources':
    from resources.lib.modules import sources
    sources.sources().alterSources(url, meta)

elif action == 'clearSources':
    from resources.lib.modules import sources
    sources.sources().clearSources()

elif action == 'random':
    rtype = params.get('rtype')
    if rtype == 'movie':
        from resources.lib.indexers import movies
        rlist = movies.movies().get(url, create_directory=False)
        r = sys.argv[0]+"?action=play"
    elif rtype == 'episode':
        from resources.lib.indexers import episodes
        rlist = episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season, create_directory=False)
        r = sys.argv[0]+"?action=play"
    elif rtype == 'season':
        from resources.lib.indexers import episodes
        rlist = episodes.seasons().get(tvshowtitle, year, imdb, tvdb, create_directory=False)
        r = sys.argv[0]+"?action=random&rtype=episode"
    elif rtype == 'show':
        from resources.lib.indexers import tvshows
        rlist = tvshows.tvshows().get(url, create_directory=False)
        r = sys.argv[0]+"?action=random&rtype=season"
    from resources.lib.modules import control
    from random import randint
    import json
    try:
        rand = randint(1,len(rlist))-1
        for p in ['title','year','imdb','tvdb','season','episode','tvshowtitle','premiered','select']:
            if rtype == "show" and p == "tvshowtitle":
                try: r += '&'+p+'='+urllib.quote_plus(rlist[rand]['title'])
                except: pass
            else:
                try: r += '&'+p+'='+urllib.quote_plus(rlist[rand][p])
                except: pass
        try: r += '&meta='+urllib.quote_plus(json.dumps(rlist[rand]))
        except: r += '&meta='+urllib.quote_plus("{}")
        if rtype == "movie":
            try: control.infoDialog(rlist[rand]['title'], control.lang(32536).encode('utf-8'), time=30000)
            except: pass
        elif rtype == "episode":
            try: control.infoDialog(rlist[rand]['tvshowtitle']+" - Season "+rlist[rand]['season']+" - "+rlist[rand]['title'], control.lang(32536).encode('utf-8'), time=30000)
            except: pass
        control.execute('RunPlugin(%s)' % r)
    except:
        control.infoDialog(control.lang(32537).encode('utf-8'), time=8000)

elif action == 'movieToLibrary':
    from resources.lib.modules import libtools
    libtools.libmovies().add(name, title, year, imdb, tmdb)

elif action == 'moviesToLibrary':
    from resources.lib.modules import libtools
    libtools.libmovies().range(url)

elif action == 'tvshowToLibrary':
    from resources.lib.modules import libtools
    libtools.libtvshows().add(tvshowtitle, year, imdb, tvdb)

elif action == 'tvshowsToLibrary':
    from resources.lib.modules import libtools
    libtools.libtvshows().range(url)

elif action == 'updateLibrary':
    from resources.lib.modules import libtools
    libtools.libepisodes().update(query)

elif action == 'service':
    from resources.lib.modules import libtools
    libtools.libepisodes().service()
#################################################################################################################################### @Cy4Root
###################
###### Radio ######
###################
elif action == 'radioNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().radio()

elif action == 'radio':
    from resources.lib.indexers import radio
    radio.radionet().get_stations(url)

elif action == 'radioCat':
    from resources.lib.indexers import radio
    radio.radionet().get_categories(url)

elif action == 'radioCatStations':
    from resources.lib.indexers import radio
    radio.radionet().get_category_stations(url)

elif action == 'radioPlayStation':
    from resources.lib.indexers import radio
    radio.radionet().play_station(url)

elif action == 'bmNavigator':
    from resources.lib.modules import jsonbm
    if url == 'channels':
        jsonbm.jsonBookmarks().show_channels()
    elif url == 'podcasts':
        jsonbm.jsonBookmarks().show_podcasts()
    elif url == 'radio':
        jsonbm.jsonBookmarks().show_radio()

elif action == 'add_channel':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().add_channel(url)

elif action == 'remove_channel':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().rem_channel(url)

elif action == 'add_podcast':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().add_podcast(url)

elif action == 'remove_podcast':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().rem_podcast(url)

elif action == 'add_radio':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().add_radio(url)

elif action == 'remove_radio':
    from resources.lib.modules import jsonbm
    jsonbm.jsonBookmarks().rem_radio(url)

###################
###### Swift ######
###################
elif action == 'swiftNavigator':
    from resources.lib.indexers import swift
    swift.swift().root()

elif action == 'swiftCat':
    from resources.lib.indexers import swift
    swift.swift().swiftCategory(url)

elif action == 'swiftPlay':
    from resources.lib.indexers import swift
    swift.swift().swiftPlay(url)

elif action == 'mytraktNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mytrakt()

elif action == 'collections':
    from resources.lib.indexers import collections
    collections.collections().get(url)  


# IPtv Navigator ##

elif action == 'iptvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().iptv()

elif action == 'directory':
    from resources.lib.indexers import iptv
    iptv.indexer().get(url)

elif action == 'qdirectory':
    from resources.lib.indexers import iptv
    iptv.indexer().getq(url)

elif action == 'xdirectory':
    from resources.lib.indexers import iptv
    iptv.indexer().getx(url)

if action == 'xxx':
    from resources.lib.indexers import iptv
    iptv.indexer().rootXXX()

if action == 'alltv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootalltv()

if action == 'cinematv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootcinematv()

if action == 'faithtv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootfaithtv()

if action == 'lodgetv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootlodgetv()

if action == 'radiotv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootradiotv()

if action == 'sportplugins':
    from resources.lib.indexers import iptv
    iptv.indexer().rootsportplugins()

if action == 'mytv':
    from resources.lib.indexers import iptv
    iptv.indexer().rootmytv()








elif action == 'acronaitv_menu':
    from resources.lib.indexers import acrotv
    acrontv.acronaitv().list_categories()

if action == 'sportChannels':
    from resources.lib.indexers import iptv
    iptv.indexer().root()







elif action == 'mytube':
    from resources.lib.indexers import youtube
    if subid == None:
        youtube.yt_index().root(action)
    else:
        youtube.yt_index().get(action, subid)

elif action == 'arconai_cable':
    from resources.lib.indexers import acrotv
    acrotv.acrotv().list_cable()

elif action == 'arconai_play':
    from resources.lib.indexers import acrotv
    acrotv.acrotv().play_video(params['selection'])

elif action == 'tmdbNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tmdb()

if action == 'boxsetsNavigator':
    from resources.lib.indexers import tmdb
    tmdb.movies().collectionBoxset()

if action == 'actorNavigator':
    from resources.lib.indexers import tmdb
    tmdb.movies().actorBoxset()

elif action == 'holidaysNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().holidaysBoxset()




elif action == 'tmdb':
    from resources.lib.indexers import tmdb
    tmdb.movies().get(url)

def toggleAll(setting, query=None, sourceList=None):
    from resources.lib.sources import getAllHosters
    sourceList = getAllHosters() if not sourceList else sourceList
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, setting)
    control.openSettings(query)


