# -*- coding: UTF-8 -*-


# Addon Name: Mirrorv2
# Addon id: plugin.video.mirrorv2
# Addon Provider: Cy4Root

import os, base64, sys, urllib2, urlparse
import xbmc, xbmcaddon, xbmcgui

from resources.lib.modules import control
from resources.lib.modules import trakt
from resources.lib.modules import cache


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1]) ; control.moderator()
artPath = control.artPath() ; addonFanart = control.addonFanart()

imdbCredentials = False if control.setting('imdb.user') == '' else True

traktCredentials = trakt.getTraktCredentialsInfo()
traktIndicators = trakt.getTraktIndicatorsInfo()

queueMenu = control.lang(32065).encode('utf-8')


class navigator:
    ADDON_ID      = xbmcaddon.Addon().getAddonInfo('id')
    HOMEPATH      = xbmc.translatePath('special://home/')
    ADDONSPATH    = os.path.join(HOMEPATH, 'addons')
    THISADDONPATH = os.path.join(ADDONSPATH, ADDON_ID)
    NEWSFILE      = base64.b64decode(b'aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3LzdSR0FKR0hL')
    LOCALNEWS     = os.path.join(THISADDONPATH, 'whatsnew.txt')
    
    def root(self):
        self.addDirectoryItem('Status', 'newsNavigator', 'icon.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32001, 'movieNavigator', 'movies.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.movietheaters') == True:
            self.addDirectoryItem(320222, 'tmdb&url=theaters', 'in-theaters.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32002, 'tvNavigator', 'tvshows.gif', 'DefaultTVShows.png')
        if (traktIndicators == True and not control.setting('tv.widget.alt') == '0') or (traktIndicators == False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.gif', 'DefaultRecentlyAddedEpisodes.png') 
        if self.getMenuEnabled('navi.boxsetsmaster') == True:
            self.addDirectoryItem('BoxSets', 'boxsetsmaster', 'boxsets.gif', 'DefaultSets.png')  
        if self.getMenuEnabled('navi.vipbox') == True:
            self.addDirectoryItem('VipBox', 'vipbox', 'vip.gif', 'fanart2.gif')
        if self.getMenuEnabled('navi.noting') == False:
            self.addDirectoryItem(32008, 'toolNavigator', 'tools.gif', 'DefaultAddonProgram.png')
            self.addDirectoryItem('Scraper Settings', 'openscrapersSettings&query=0.0', 'openscrapers.gif', 'DefaultAddonProgram.png')
        downloads = True if control.setting('downloads') == 'true' and (len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
        if downloads == True:
            self.addDirectoryItem(32009, 'downloadNavigator', 'downloads.gif', 'DefaultFolder.png')
	#self.addDirectoryItem('Providers', 'liptonscrapersettings&query=2.0', 'module.png', 'DefaultAddonService.png', isFolder=False)
        self.addDirectoryItem(32010, 'searchNavigator', 'search.gif', 'DefaultFolder.png')
        self.endDirectory()

    def getMenuEnabled(self, menu_title):
        is_enabled = control.setting(menu_title).strip()
        if (is_enabled == '' or is_enabled == 'false'): return False
        return True

#######################################################################

    def news(self):
            message=self.open_news_url(self.NEWSFILE)
            r = open(self.LOCALNEWS)
            compfile = r.read()       
            if len(message)>1:
                    if compfile == message:pass
                    else:
                            text_file = open(self.LOCALNEWS, "w")
                            text_file.write(message)
                            text_file.close()
                            compfile = message
            self.showText('[COLOR yellow]ONLINE STATUS:[/COLOR] [B][COLOR green]GOOD[/COLOR][/B]', compfile)
    def open_news_url(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'klopp')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            print link
            return link

    def news_local(self):
            r = open(self.LOCALNEWS)
            compfile = r.read()
            self.showText('[B]Updates and Information[/B]', compfile)

    def showText(self, heading, text):
        id = 10147
        xbmc.executebuiltin('ActivateWindow(%d)' % id)
        xbmc.sleep(500)
        win = xbmcgui.Window(id)
        retry = 50
        while (retry > 0):
            try:
                xbmc.sleep(10)
                retry -= 1
                win.getControl(1).setLabel(heading)
                win.getControl(5).setText(text)
                quit()
                return
            except: pass

#######################################################################

    def movies(self, lite=False):
 	if lite == False:
            if not control.setting('lists.widget') == '0':
                   self.addDirectoryItem(32003, 'mymovieliteNavigator', 'mymovies.gif', 'DefaultVideoPlaylists.png')
        if self.getMenuEnabled('navi.movietrending') == True:
            self.addDirectoryItem(32017, 'movies&url=trending', 'people-watching.gif', 'DefaultRecentlyAddedMovies.png')
        if self.getMenuEnabled('navi.moviepopular') == True:
            self.addDirectoryItem(32018, 'movies&url=popular', 'most-popular.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.movieviews') == True:
            self.addDirectoryItem(32019, 'movies&url=views', 'most-voted.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.movieoscars') == True:
            self.addDirectoryItem(32021, 'movies&url=oscars', 'oscar-winners.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.movietheaters') == True:
            self.addDirectoryItem(32022, 'movies&url=theaters', 'in-theaters.gif', 'DefaultRecentlyAddedMovies.png')
        if self.getMenuEnabled('navi.moviewidget') == True:
            self.addDirectoryItem(32005, 'movieWidget', 'latest-movies.gif', 'DefaultRecentlyAddedMovies.png')
        if self.getMenuEnabled('navi.movieyears') == True:
            self.addDirectoryItem(32012, 'movieYears', 'years.gif', 'DefaultMovies.png') 
            self.addDirectoryItem('1950 - 1959', 'movies&url=fiftys', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('1960 - 1969', 'movies&url=sixtys', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('1970 - 1979', 'movies&url=seventys', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('1980 - 1989', 'movies&url=eightys', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('1990 - 1999', 'movies&url=ninetys', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('2000 - 2009', 'movies&url=twothousand', 'years.gif', 'DefaultMovies.png')
            self.addDirectoryItem('2010 - 2019', 'movies&url=twothousand2', 'years.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.moviereview') == True:
            self.addDirectoryItem(32623, 'movieReviews', 'reviews.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.moviegenre') == True:
            self.addDirectoryItem(32011, 'movieGenres', 'genres.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.moviepersons') == True:
            self.addDirectoryItem(32013, 'moviePersons', 'people.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.movielanguages') == True:
            self.addDirectoryItem(32014, 'movieLanguages', 'languages.gif', 'DefaultMovies.png')
        if self.getMenuEnabled('navi.moviecerts') == True:
            self.addDirectoryItem(32015, 'movieCertificates', 'certificates.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.gif', 'DefaultMovies.png')

        self.endDirectory()


    def mymovies(self, lite=False):
        self.accountCheck()

        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.gif', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.gif', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32034, 'movies&url=imdbwatchlist', 'imdb.gif', 'DefaultMovies.png', queue=True)

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.gif', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.gif', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.gif', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.gif', 'DefaultMovies.png', queue=True)

        if traktCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=traktfeatured', 'trakt.gif', 'DefaultMovies.png', queue=True)

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.gif', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.gif', 'DefaultMovies.png', queue=True)

        self.addDirectoryItem(32039, 'movieUserlists', 'userlists.getTraktCredentialsInfo', 'DefaultMovies.png')

        if lite == False:
            self.addDirectoryItem(32031, 'movieliteNavigator', 'movies.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.gif', 'DefaultMovies.png')

        self.endDirectory()


    def tvshows(self, lite=False):
	if lite == False:
            if not control.setting('lists.widget') == '0':
                self.addDirectoryItem(32004, 'mytvliteNavigator', 'mytvshows.gif', 'DefaultVideoPlaylists.png')
        if self.getMenuEnabled('navi.movieyears') == True:
            self.addDirectoryItem('1950 - 1959', 'tvshows&url=fiftyst', 'years.gif', 'DefaultTVShows.png')
            self.addDirectoryItem('1960 - 1969', 'tvshows&url=sixtyst', 'years.gif', 'DefaultTVShows.png')
            self.addDirectoryItem('1970 - 1979', 'tvshows&url=seventyst', 'years.gif', 'DefaultTVShows.png')
            self.addDirectoryItem('1980 - 1989', 'tvshows&url=eightyst', 'years.gif', 'DefaultTVShows.png')
            self.addDirectoryItem('1990 - 1999', 'tvshows&url=ninetyst', 'years.gif', 'DefaultTVShows.png')
            self.addDirectoryItem('2000 - 2009', 'tvshows&url=twothousandt', 'years.gif', 'DefaultTVShows.png')
   	    self.addDirectoryItem('2010 - 2019', 'tvshows&url=twothousandt2', 'years.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvReviews') == True:
            self.addDirectoryItem(32623, 'tvReviews', 'reviews.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvGenres') == True:
            self.addDirectoryItem(32011, 'tvGenres', 'genres.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvNetworks') == True:
            self.addDirectoryItem(32016, 'tvNetworks', 'networks.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvLanguages') == True:
            self.addDirectoryItem(32014, 'tvLanguages', 'languages.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvCertificates') == True:
            self.addDirectoryItem(32015, 'tvCertificates', 'certificates.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvTrending') == True:
            self.addDirectoryItem(32017, 'tvshows&url=trending', 'people-watching.gif', 'DefaultRecentlyAddedEpisodes.png')
        if self.getMenuEnabled('navi.tvPopular') == True:
            self.addDirectoryItem(32018, 'tvshows&url=popular', 'most-popular.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvRating') == True:
            self.addDirectoryItem(32023, 'tvshows&url=rating', 'highly-rated.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvViews') == True:
            self.addDirectoryItem(32019, 'tvshows&url=views', 'most-voted.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvAiring') == True:
            self.addDirectoryItem(32024, 'tvshows&url=airing', 'airing-today.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvActive') == True:
            self.addDirectoryItem(32025, 'tvshows&url=active', 'returning-tvshows.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvPremier') == True:
            self.addDirectoryItem(32026, 'tvshows&url=premiere', 'new-tvshows.gif', 'DefaultTVShows.png')
        if self.getMenuEnabled('navi.tvAdded') == True:
            self.addDirectoryItem(32006, 'calendar&url=added', 'latest-episodes.gif', 'DefaultRecentlyAddedEpisodes.png', queue=True)
        if self.getMenuEnabled('navi.tvCalendar') == True:
            self.addDirectoryItem(32027, 'calendars', 'calendar.gif', 'DefaultRecentlyAddedEpisodes.png')
            self.addDirectoryItem(32028, 'tvPerson', 'people-search.gif', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.gif', 'DefaultTVShows.png')

        self.endDirectory()

    def mytvshows(self, lite=False):
        self.accountCheck()

        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.gif', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.gif', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32034, 'tvshows&url=imdbwatchlist', 'imdb.gif', 'DefaultTVShows.png')

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.gif', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.gif', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.gif', 'DefaultTVShows.png')
            self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.gif', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=traktfeatured', 'trakt.gif', 'DefaultTVShows.png')

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=trending', 'imdb.gif', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.gif', 'DefaultTVShows.png', queue=True)
            self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.gif', 'DefaultRecentlyAddedEpisodes.png', queue=True)
            self.addDirectoryItem(32038, 'calendar&url=mycalendar', 'trakt.gif', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        self.addDirectoryItem(32040, 'tvUserlists', 'userlists.gif', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32041, 'episodeUserlists', 'userlists.gif', 'DefaultTVShows.png')

        if lite == False:
            self.addDirectoryItem(32031, 'tvliteNavigator', 'tvshows.gif', 'DefaultTVShows.png')
            self.addDirectoryItem(32028, 'tvPerson', 'people-search.gif', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.gif', 'DefaultTVShows.png')

        self.endDirectory()

    

    def tools(self):
        self.addDirectoryItem(32043, 'openSettings&query=1.0', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32083, 'providersettings&query=2.0', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32556, 'libraryNavigator', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32049, 'viewsNavigator', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32050, 'clearSources', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32604, 'clearCacheSearch', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32052, 'clearCache', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32614, 'clearMetaCache', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32613, 'clearAllCache', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32073, 'authTrakt', 'trakt.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32609, 'urlResolver', 'urlresolver.gif', 'DefaultAddonProgram.png')

        self.endDirectory()

    def library(self):
        self.addDirectoryItem(32557, 'openSettings&query=5.0', 'tools.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32558, 'updateLibrary&query=tool', 'library_update.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32559, control.setting('library.movie'), 'movies.gif', 'DefaultMovies.png', isAction=False)
        self.addDirectoryItem(32560, control.setting('library.tv'), 'tvshows.gif', 'DefaultTVShows.png', isAction=False)

        if trakt.getTraktCredentialsInfo():
            self.addDirectoryItem(32561, 'moviesToLibrary&url=traktcollection', 'trakt.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32562, 'moviesToLibrary&url=traktwatchlist', 'trakt.gif', 'DefaultMovies.png')
            self.addDirectoryItem(32563, 'tvshowsToLibrary&url=traktcollection', 'trakt.gif', 'DefaultTVShows.png')
            self.addDirectoryItem(32564, 'tvshowsToLibrary&url=traktwatchlist', 'trakt.gif', 'DefaultTVShows.png')

        self.endDirectory()

    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')

        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.gif', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.gif', 'DefaultTVShows.png', isAction=False)

        self.endDirectory()

    def radio(self):
        try:
            self.addDirectoryItem('localstations', 'radio&url=localstations', 'podcast.gif', 'DefaultVideoPlaylists.png')
            self.addDirectoryItem('recommended', 'radio&url=recommended', 'podcast.gif', 'DefaultVideoPlaylists.png')
            self.addDirectoryItem('tophundred', 'radio&url=tophundred', 'podcast.gif', 'DefaultVideoPlaylists.png')
	    self.addDirectoryItem('country', 'radioCat&url=country', 'podcast.gif', 'DefaultVideoPlaylists.png')
            self.addDirectoryItem('language', 'radioCat&url=language', 'podcast.gif', 'DefaultVideoPlaylists.png')
	    self.endDirectory()
        except Exception:
            pass

    def boxsetsmaster(self):
        self.addDirectoryItem('[COLOR=gold]BoxSets Collection [/COLOR]','tmdb', 'boxsets.gif', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem(32034, 'movieimdbUserLists', 'imdb.gif', 'DefaultMovies.png')
        self.addDirectoryItem(32635,  'boxsetsNavigator', 'movies.gif', 'DefaultMovies.png')
	self.addDirectoryItem(30324, 'tvshows&url=tvshowcoll', 'tvshows.png', 'DefaultVideoPlaylists.png')					
	self.addDirectoryItem(32092, 'holidaysNavigator', 'calendar.gif', 'DefaultMovies.png')
	self.addDirectoryItem(32094, 'collections&url=disneymovies2', 'kids.gif', 'DefaultMovies.png')
	self.addDirectoryItem(30323, 'kidsboxsets', 'kids.gif', 'DefaultMovies.png')
        self.addDirectoryItem(32091, 'actorNavigator', 'genres.gif', 'DefaultMovies.png')
        self.addDirectoryItem(32641, 'mysupermvNavigator', 'fitness.gif', 'DefaultMovies.png')	
        self.addDirectoryItem('[COLOR=darkorange]BoxSets Selection[/COLOR]','tmdb', 'boxsets.gif', 'DefaultVideoPlaylists.png')
	self.addDirectoryItem(32632, 'collections&url=moviemirror', 'tmdb.gif', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem(30335, 'movieimdbUserLists', 'imdb.gif', 'DefaultMovies.png')
	self.addDirectoryItem(32093, 'collections&url=netflixmovies', 'tmdb.gif', 'DefaultMovies.png')
	self.addDirectoryItem(32633, 'collections&url=kidsboxcollection2', 'kids.gif', 'DefaultVideoPlaylists.png')
	self.addDirectoryItem(30325, 'genremovies', 'genres.gif', 'DefaultVideoPlaylists.png')
        self.endDirectory()

    def imdbLists(self):
        self.addDirectoryItem('Explore Keywords(Movies)', 'movieExploreKeywords', 'imdb.gif', 'DefaultMovies.png')
        self.addDirectoryItem('Explore Keywords(TV Shows)', 'tvshowExploreKeywords', 'imdb.gif', 'DefaultTVShows.png')
        self.addDirectoryItem('Explore UserLists(Movies)', 'movieimdbUserLists', 'imdb.gif', 'DefaultMovies.png')
        self.addDirectoryItem('Explore UserLists(TV Shows)', 'tvshowimdbUserLists', 'imdb.gif', 'DefaultTVShows.png')
        self.addDirectoryItem('Hella LifeTime & HallMark Movies', 'hellaLifeTimeHallMark', 'userlists.gif', 'DefaultVideoPlaylists.png')
        self.endDirectory()

    def genremovies(self):
        self.addDirectoryItem('Horror (2019 - 2000)','movies&url=tophorr', 'movies.gif', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem('Horror (Top 50 1980s)', 'collections&url=horror80s', 'tmdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30326, 'movies&url=collectionshackers', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30327, 'movies&url=collectionscrime', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30328, 'movies&url=collectionsprison', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30329, 'collections&url=musical', 'tmdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30330, 'movies&url=collectionsromance', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30331, 'movies&url=collectionswestern', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
	self.addDirectoryItem(30338, 'movies&url=collectionsinterhindi', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
	self.addDirectoryItem(30336, 'movies&url=collectionsforeign', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
	self.addDirectoryItem(30337, 'movies&url=collectionspsychological', 'imdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.endDirectory()


    def iptv(self):
        self.addDirectoryItem('World Tv', 'worldtv', 'networks.gif', 'fanart.jpg')
        self.addDirectoryItem('AllTV', 'alltv', 'networks.gif', 'fanart.jpg')
        self.addDirectoryItem('CinemaTV', 'cinematv', 'networks.gif', 'fanart.jpg')
	self.addDirectoryItem('FaithTV', 'faithtv', 'networks.gif', '')
	self.addDirectoryItem('LodgeTV', 'lodgetv', 'networks.gif', '')
	self.addDirectoryItem('AcroTV',  'arconai_cable',  'networks.gif',  'DefaultTVShows.png')
	self.addDirectoryItem('MyTV',  'mytv',  'networks.gif',  'DefaultTVShows.png')     
	self.endDirectory()

    def vipbox(self):
        self.addDirectoryItem('oneclick', 'oneclick', 'networks.gif', 'DefaultRecentlyAddedMovies.png')   
        self.addDirectoryItem('random', 'random&rtype=movies&url=popular', 'library_update.gif', 'DefaultRecentlyAddedMovies.png')   
	self.addDirectoryItem('Iptv', 'iptvNavigator', 'networks.gif', 'fanart.jpg') 
        self.addDirectoryItem('Sport&Tv', 'sportplugins', 'networks.gif', 'fanart.jpg')  
        self.addDirectoryItem('Documentary', 'docuNavigator', 'channels.gif', 'DefaultMovies.png')
   	self.addDirectoryItem('Radio', 'radioNavigator', 'airing-today.gif', 'DefaultVideoPlaylists.png')
 	self.addDirectoryItem('Music Choice', 'mclist', 'channels.gif', 'DefaultMovies.png')
        self.addDirectoryItem('kidscorner', 'kidscorner', 'kids.gif', 'DefaultMovies.png')
        self.addDirectoryItem('fitness', 'fitness', 'fitness.gif', 'DefaultMovies.png')
        self.addDirectoryItem('legends', 'legends', 'legends.gif', 'DefaultMovies.png')
        self.addDirectoryItem('Youtube', 'mytube', 'youtube.gif', 'youtubemenu.png') #(root.txt)  
	if self.getMenuEnabled('navi.xxx') == True:
            self.addDirectoryItem('[COLOR pink]Adult\'s Only[/COLOR]', 'xxx', 'highly-rated.gif', 'DefaultTVShows.png')  
        self.endDirectory()

    def oneclickmovies(self):
    	self.addDirectoryItem(33003, '1click', 'debrid.gif', 'debrid.png')  
        self.addDirectoryItem(33002, '1kmovies', '1k.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(33004, 'dtsmovies', 'dts.jpg', 'debrid.png')  
        self.addDirectoryItem(33001, '4kmovies', '4k.jpeg', 'DefaultMovies.png')
        self.addDirectoryItem(33020, 'vipclick', 'vip.gif', 'DefaultMovies.png')
	if self.getMenuEnabled('navi.1clicknl') == True:
            self.addDirectoryItem(33006, 'nlmovie', 'dutch.png', 'debrid.png')  
            self.addDirectoryItem(30332, 'nltvshow', 'dutch.png', 'debrid.png')  
        self.addDirectoryItem(33005, 'kids', 'kidscorner.gif', 'kidscorner.png')  
        self.endDirectory()
	
    def holidaysBoxset(self):
        self.addDirectoryItem(32095, 'collections&url=xmasmovies2', 'tmdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32096, 'collections&url=eastermovies', 'tmdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32097, 'collections&url=halloweenmovies', 'tmdb.gif', 'DefaultRecentlyAddedMovies.png')
        self.endDirectory()


    def providersettings(self):
        self.addDirectoryItem('[COLOR=gold]Under the settings menu you can switch from Providers (Click Here) [/COLOR]','openSettings&query=1.0', 'tools.gif', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem('OpenScraper Settings (Default)', 'openscrapersSettings&query=0.0', 'openscrapers.gif', 'DefaultAddonProgram.png')
        self.addDirectoryItem('LiptonModule Settings', 'liptonscrapersettings&query=0.0', 'module.png', 'DefaultAddonProgram.png')
        self.endDirectory()

    def search(self):
        self.addDirectoryItem(32001, 'movieSearch', 'search.gif', 'DefaultMovies.png')
        self.addDirectoryItem(32002, 'tvSearch', 'search.gif', 'DefaultTVShows.png')
        self.addDirectoryItem(32029, 'moviePerson', 'people-search.gif', 'DefaultMovies.png')
        self.addDirectoryItem(32030, 'tvPerson', 'people-search.gif', 'DefaultTVShows.png')

        self.endDirectory()

    def views(self):
        try:
            control.idle()

            items = [ (control.lang(32001).encode('utf-8'), 'movies'), (control.lang(32002).encode('utf-8'), 'tvshows'), (control.lang(32054).encode('utf-8'), 'seasons'), (control.lang(32038).encode('utf-8'), 'episodes') ]

            select = control.selectDialog([i[0] for i in items], control.lang(32049).encode('utf-8'))

            if select == -1: return

            content = items[select][1]

            title = control.lang(32059).encode('utf-8')
            url = '%s?action=addView&content=%s' % (sys.argv[0], content)

            poster, banner, fanart = control.addonPoster(), control.addonBanner(), control.addonFanart()

            item = control.item(label=title)
            item.setInfo(type='Video', infoLabels = {'title': title})
            item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
            item.setProperty('Fanart_Image', fanart)

            control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=False)
            control.content(int(sys.argv[1]), content)
            control.directory(int(sys.argv[1]), cacheToDisc=True)

            from resources.lib.modules import views
            views.setView(content, {})
        except:
            return


    def accountCheck(self):
        if traktCredentials == False and imdbCredentials == False:
            control.idle()
            control.infoDialog(control.lang(32042).encode('utf-8'), sound=True, icon='WARNING')
            sys.exit()


    def infoCheck(self, version):
        try:
            control.infoDialog('', control.lang(32074).encode('utf-8'), time=5000, sound=False)
            return '1'
        except:
            return '1'


    def clearCache(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')

    def clearCacheMeta(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache

        cache.cache_clear_meta()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')

    def clearCacheProviders(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_providers()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')

    def clearCacheSearch(self):
        control.idle()
        if control.yesnoDialog(control.lang(32056).encode('utf-8'), '', ''):
            control.setSetting('tvsearch', '')
            control.setSetting('moviesearch', '')
            control.refresh()

    def clearCacheAll(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_all()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        thumb = os.path.join(artPath, thumb) if not artPath == None else icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def Toggle_Dbird(self):
        HMMMPATH = xbmc.translatePath(os.path.join('special://home/addons/', 'script.module.resolveurl'))
        ummmDialog = xbmcgui.Dialog()
        if not os.path.exists(HMMMPATH):
            ummmDialog("ummmm", "There was a error loading script.module.resolveurl.")
            sys.exit()
        try:
            if xbmcaddon.Addon('script.module.resolveurl').getSetting('RealDebridResolver_enabled') != 'true':
                try:
                    xbmcaddon.Addon('script.module.resolveurl') .setSetting(id='RealDebridResolver_enabled', value='true')
                    control.refresh()
                    ummmDialog.notification('[B]Turn On[/B] RealDebridResolver', 'Done, Setting [B]Enabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except: pass
            elif xbmcaddon.Addon('script.module.resolveurl').getSetting('RealDebridResolver_enabled') != 'false':
                try:
                    xbmcaddon.Addon('script.module.resolveurl') .setSetting(id='RealDebridResolver_enabled', value='false')
                    control.refresh()
                    ummmDialog.notification('[B]Turn Off[/B] RealDebridResolver', 'Done, Setting [B]Disabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except: pass
        except:
            pass


    def Toggle_Adbird(self):
        HMMMPATH = xbmc.translatePath(os.path.join('special://home/addons/', 'script.module.resolveurl'))
        ummmDialog = xbmcgui.Dialog()
        if not os.path.exists(HMMMPATH):
            ummmDialog("ummmm", "There was a error loading script.module.resolveurl.")
            sys.exit()
        try:
            if xbmcaddon.Addon('script.module.resolveurl').getSetting('AllDebridResolver_enabled') != 'true':
                try:
                    xbmcaddon.Addon('script.module.resolveurl') .setSetting(id='AllDebridResolver_enabled', value='true')
                    control.refresh()
                    ummmDialog.notification('[B]Turn On[/B] AllDebridResolver', 'Done, Setting [B]Enabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except: pass
            elif xbmcaddon.Addon('script.module.resolveurl').getSetting('AllDebridResolver_enabled') != 'false':
                try:
                    xbmcaddon.Addon('script.module.resolveurl') .setSetting(id='AllDebridResolver_enabled', value='false')
                    control.refresh()
                    ummmDialog.notification('[B]Turn Off[/B] AllDebridResolver', 'Done, Setting [B]Disabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except: pass
        except:
            pass


    def Toggle_PreMe(self):
        HMMMPATH = xbmc.translatePath(os.path.join('special://home/addons/', 'script.module.resolveurl'))
        ummmDialog = xbmcgui.Dialog()
        if not os.path.exists(HMMMPATH):
            ummmDialog("ummmm", "There was a error loading script.module.resolveurl.")
            sys.exit()
        try:
            if xbmcaddon.Addon('script.module.resolveurl').getSetting('PremiumizeMeResolver_enabled') != 'true':
                try:
                    xbmcaddon.Addon('script.module.resolveurl').setSetting(id='PremiumizeMeResolver_enabled', value='true')
                    control.refresh()
                    ummmDialog.notification('[B]Turn On[/B] PremiumizeMeResolver', 'Done, Setting [B]Enabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except:
                    pass
            elif xbmcaddon.Addon('script.module.resolveurl').getSetting('PremiumizeMeResolver_enabled') != 'false':
                try:
                    xbmcaddon.Addon('script.module.resolveurl').setSetting(id='PremiumizeMeResolver_enabled', value='false')
                    control.refresh()
                    ummmDialog.notification('[B]Turn Off[/B] PremiumizeMeResolver', 'Done, Setting [B]Disabled[/B].', xbmcgui.NOTIFICATION_INFO, 5000)
                except:
                    pass
        except:
            pass

    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)



