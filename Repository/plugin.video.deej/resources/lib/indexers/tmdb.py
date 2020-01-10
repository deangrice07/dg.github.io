# -*- coding: utf-8 -*-

import os,sys,re,json,urllib,urlparse,base64,datetime,unicodedata
from resources.lib.modules import trakt,control,client,cache,metacache
from resources.lib.modules import playcount,workers,views


sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
artPath = control.artPath()
addonFanart = control.addonFanart()
imdbCredentials = False if control.setting('imdb.user') == '' else True
traktCredentials = trakt.getTraktCredentialsInfo()
traktIndicators = trakt.getTraktIndicatorsInfo()
queueMenu = control.lang(32065).encode('utf-8')

try:
    action = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))['action']
except:
    action = None


class movies:
    def __init__(self):
        self.list = []
        self.tmdb_link = 'https://api.themoviedb.org'
        self.trakt_link = 'https://api.trakt.tv'
        self.imdb_link = 'http://www.imdb.com'
        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = base64.b64decode('NTY3NzY4YzZjZWNkNjdlNTkyZTFhZjk2OGViYjdjZDk=')
        self.omdb_key = control.setting('omdb.key')
        if self.omdb_key == '' or self.omdb_key == None:
            self.omdb_key = '74703860'
        self.trakt_user = re.sub('[^a-z0-9]', '-', control.setting('trakt.user').strip().lower())
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.tmdb_lang = 'en'
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.year_date = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.tmdb_info_link = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,releases,external_ids' % ('%s', self.tmdb_key, self.tmdb_lang)
        self.tmdb_by_query_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ("%s", self.tmdb_key)
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s&apikey=%s' % ("%s", "%s", self.omdb_key)
        self.imdbinfo = 'http://www.omdbapi.com/?i=%s&plot=full&r=json&apikey=%s' % ("%s", self.omdb_key)
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.search_link = 'https://api.themoviedb.org/3/search/movie?&api_key=%s&query=%s'

        self.popular_link = 'https://api.themoviedb.org/3/movie/popular?api_key=%s&page=1' % self.tmdb_key
        self.toprated_link = 'https://api.themoviedb.org/3/movie/top_rated?api_key=%s&page=1' % self.tmdb_key
        self.featured_link = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&primary_release_date.gte=date[365]&primary_release_date.lte=date[60]&page=1' % self.tmdb_key
        self.theaters_link = 'https://api.themoviedb.org/3/movie/now_playing?api_key=%s&page=1' % self.tmdb_key
        self.premiere_link = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&first_air_date.gte=%s&first_air_date.lte=%s&page=1' % (self.tmdb_key, self.year_date, self.today_date)
        self.tmdbUserLists_link = 'https://api.themoviedb.org/3/list/%s?api_key=%s' % ("%s", self.tmdb_key)



    def get(self, url, idx=True):
        try:
            try:
                url = getattr(self, url + '_link')
            except:
                pass
            try:
                u = urlparse.urlparse(url).netloc.lower()
            except:
                pass
            if u in self.tmdb_link:
                self.list = cache.get(self.tmdb_list, 24, url)
                self.worker()
            elif u in self.trakt_link and '/users/' in url:
                try:
                    if url == self.trakthistory_link:
                        raise Exception()
                    if not '/%s/' % self.trakt_user in url:
                        raise Exception()
                    if trakt.getActivity() > cache.timeout(self.trakt_list, url):
                        raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url)
                except:
                    self.list = cache.get(self.trakt_list, 0, url)
                if '/%s/' % self.trakt_user in url:
                    self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))
                if idx == True:
                    self.worker()
            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url)
                if idx == True:
                    self.worker()
            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 0, url)
                if idx == True:
                    self.worker()
            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                if idx == True:
                    self.worker()
            if idx == True:
                self.movieDirectory(self.list)
            return self.list
        except:
            pass


########################################################################################################################################################

# tmdb.movies().collectionBoxset()
    def collectionBoxset(self):
        self.addDirectoryItem(' 48 Hrs. (1982-1990)', 'collections&url=fortyeighthours', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Ace Ventura. (1994-1995)', 'collections&url=aceventura', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Airplane  (1980-1982)', 'collections&url=airplane', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Airport  (1970-1979)', 'collections&url=airport', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' American Graffiti  (1973-1979)', 'collections&url=americangraffiti', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Anaconda  (1997-2004)', 'collections&url=anaconda', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Analyze This  (1999-2002)', 'collections&url=analyzethis', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Anchorman  (2004-2013)', 'collections&url=anchorman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Austin Powers  (1997-2002)', 'collections&url=austinpowers', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Avengers  (2008-2017)', 'collections&url=avengers', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Back to the Future  (1985-1990)', 'collections&url=backtothefuture', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Bad Boys  (1995-2003)', 'collections&url=badboys', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Bad Santa  (2003-2016)', 'collections&url=badsanta', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Basic Instinct  (1992-2006)', 'collections&url=basicinstinct', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Batman  (1989-2016)', 'collections&url=batman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Beverly Hills Cop  (1984-1994)', 'collections&url=beverlyhillscop', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Big Mommas House  (2000-2011)', 'collections&url=bigmommashouse', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Blues Brothers  (1980-1998)', 'collections&url=bluesbrothers', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Bourne  (2002-2016)', 'collections&url=bourne', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Bruce Almighty  (2003-2007)', 'collections&url=brucealmighty', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Caddyshack  (1980-1988)', 'collections&url=caddyshack', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Cheaper by the Dozen  (2003-2005)', 'collections&url=cheaperbythedozen', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Cheech and Chong  (1978-1984)', 'collections&url=cheechandchong', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Childs Play  (1988-2004)', 'collections&url=childsplay', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' City Slickers  (1991-1994)', 'collections&url=cityslickers', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Conan  (1982-2011)', 'collections&url=conan', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Crank  (2006-2009)', 'collections&url=crank', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Crocodile Dundee  (1986-2001)', 'collections&url=crodiledunde', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Da Vinci Code  (2006-2017)', 'collections&url=davincicode', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Daddy Day Care  (2003-2007)', 'collections&url=daddydaycare', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Dark Knight Trilogy  (2005-2013)', 'collections&url=darkknight', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Death Wish  (1974-1994)', 'collections&url=deathwish', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Delta Force  (1986-1990)', 'collections&url=deltaforce', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Die Hard  (1988-2013)', 'collections&url=diehard', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Dirty Dancing  (1987-2004)', 'collections&url=dirtydancing', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Dirty Harry  (1971-1988)', 'collections&url=dirtyharry', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Dumb and Dumber  (1994-2014)', 'collections&url=dumbanddumber', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Escape from New York  (1981-1996)', 'collections&url=escapefromnewyork', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Every Which Way But Loose  (1978-1980)', 'collections&url=everywhichwaybutloose', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Exorcist  (1973-2005)', 'collections&url=exorcist', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Expendables  (2010-2014)', 'collections&url=theexpendables', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Fantastic Four  (2005-2015)', 'collections&url=fantasticfour', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Fast and the Furious  (2001-2017)', 'collections&url=fastandthefurious', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Father of the Bride  (1991-1995)', 'collections&url=fatherofthebride', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Fletch  (1985-1989)', 'collections&url=fletch', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Friday  (1995-2002)', 'collections&url=friday', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Friday the 13th  (1980-2009)', 'collections&url=fridaythe13th', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Fugitive  (1993-1998)', 'collections&url=fugitive', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' G.I. Joe  (2009-2013)', 'collections&url=gijoe', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Get Shorty  (1995-2005)', 'collections&url=getshorty', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Gettysburg  (1993-2003)', 'collections&url=gettysburg', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Ghost Rider  (2007-2011)', 'collections&url=ghostrider', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Ghostbusters  (1984-2016)', 'collections&url=ghostbusters', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Gods Not Dead  (2014-2016)', 'collections&url=godsnotdead', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Godfather  (1972-1990)', 'collections&url=godfather', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Godzilla  (1956-2016)', 'collections&url=godzilla', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Grown Ups  (2010-2013)', 'collections&url=grownups', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Grumpy Old Men  (2010-2013)', 'collections&url=grumpyoldmen', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Guns of Navarone  (1961-1978)', 'collections&url=gunsofnavarone', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Halloween  (1978-2009)', 'collections&url=halloween', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hangover  (2009-2013)', 'collections&url=hangover', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hannibal Lector  (1986-2007)', 'collections&url=hanniballector', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hellraiser  (1987-1996)', 'collections&url=hellraiser', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Honey I Shrunk the Kids  (1989-1995)', 'collections&url=honeyishrunkthekids', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Horrible Bosses  (2011-2014)', 'collections&url=horriblebosses', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hostel  (2005-2011)', 'collections&url=hostel', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hot Shots  (1991-1996)', 'collections&url=hotshots', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Hulk  (2003-2008)', 'collections&url=hulk', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Independence Day  (1996-2016)', 'collections&url=independenceday', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Indiana Jones  (1981-2008)', 'collections&url=indianajones', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Insidious  (2010-2015)', 'collections&url=insidious', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Iron Eagle  (1986-1992)', 'collections&url=ironeagle', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Iron Man  (2008-2013)', 'collections&url=ironman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jack Reacher  (2012-2016)', 'collections&url=jackreacher', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jack Ryan  (1990-2014)', 'collections&url=jackryan', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jackass  (2002-2013)', 'collections&url=jackass', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' James Bond  (1963-2015)', 'collections&url=jamesbond', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jaws  (1975-1987)', 'collections&url=jaws', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jeepers Creepers  (2001-2017)', 'collections&url=jeeperscreepers', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' John Wick  (2014-2017)', 'collections&url=johnwick', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jumanji  (1995-2005)', 'collections&url=jumanji', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Jurassic Park  (1993-2015)', 'collections&url=jurassicpark', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Kick-Ass  (2010-2013)', 'collections&url=kickass', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Kill Bill  (2003-2004)', 'collections&url=killbill', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' King Kong  (1933-2016)', 'collections&url=kingkong', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Lara Croft  (2001-2003)', 'collections&url=laracroft', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Legally Blonde  (2001-2003)', 'collections&url=legallyblonde', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Lethal Weapon  (1987-1998)', 'collections&url=leathalweapon', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Look Whos Talking  (1989-1993)', 'collections&url=lookwhostalking', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Machete  (2010-2013)', 'collections&url=machete', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Magic Mike  (2012-2015)', 'collections&url=magicmike', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Major League  (1989-1998)', 'collections&url=majorleague', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Man from Snowy River  (1982-1988)', 'collections&url=manfromsnowyriver', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Mask  (1994-2005)', 'collections&url=mask', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Matrix  (1999-2003)', 'collections&url=matrix', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Mechanic  (2011-2016)', 'collections&url=themechanic', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Meet the Parents  (2000-2010)', 'collections&url=meettheparents', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Men in Black  (1997-2012)', 'collections&url=meninblack', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Mighty Ducks  (1995-1996)', 'collections&url=mightyducks', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Miss Congeniality  (2000-2005)', 'collections&url=misscongeniality', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Missing in Action  (1984-1988)', 'collections&url=missinginaction', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Mission Impossible  (1996-2015)', 'collections&url=missionimpossible', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Naked Gun  (1988-1994)', 'collections&url=nakedgun', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' National Lampoon  (1978-2006)', 'collections&url=nationallampoon', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' National Lampoons Vacation  (1983-2015)', 'collections&url=nationallampoonsvacation', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' National Treasure  (2004-2007)', 'collections&url=nationaltreasure', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Neighbors  (2014-2016)', 'collections&url=neighbors', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Night at the Museum  (2006-2014)', 'collections&url=nightatthemuseum', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Nightmare on Elm Street  (1984-2010)', 'collections&url=nightmareonelmstreet', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Now You See Me  (2013-2016)', 'collections&url=nowyouseeme', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Nutty Professor  (1996-2000)', 'collections&url=nuttyprofessor', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Oceans Eleven  (2001-2007)', 'collections&url=oceanseleven', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Odd Couple  (1968-1998)', 'collections&url=oddcouple', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Oh, God  (1977-1984)', 'collections&url=ohgod', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Olympus Has Fallen  (2013-2016)', 'collections&url=olympushasfallen', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Omen  (1976-1981)', 'collections&url=omen', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Paul Blart Mall Cop  (2009-2015)', 'collections&url=paulblart', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Pirates of the Caribbean  (2003-2017)', 'collections&url=piratesofthecaribbean', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Planet of the Apes  (1968-2014)', 'collections&url=planetoftheapes', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Police Academy  (1984-1994)', 'collections&url=policeacademy', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Poltergeist  (1982-1988)', 'collections&url=postergeist', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Porkys  (1981-1985)', 'collections&url=porkys', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Predator  (1987-2010)', 'collections&url=predator', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Purge  (2013-2016)', 'collections&url=thepurge', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Rambo  (1982-2008)', 'collections&url=rambo', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' RED  (2010-2013)', 'collections&url=red', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Revenge of the Nerds  (1984-1987)', 'collections&url=revengeofthenerds', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Riddick  (2000-2013)', 'collections&url=riddick', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Ride Along  (2014-2016)', 'collections&url=ridealong', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Ring  (2002-2017)', 'collections&url=thering', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' RoboCop  (1987-1993)', 'collections&url=robocop', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Rocky  (1976-2015)', 'collections&url=rocky', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Romancing the Stone  (1984-1985)', 'collections&url=romancingthestone', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Rush Hour  (1998-2007)', 'collections&url=rushhour', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Santa Clause  (1994-2006)', 'collections&url=santaclause', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Saw  (2004-2010)', 'collections&url=saw', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Sex and the City  (2008-2010)', 'collections&url=sexandthecity', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Shaft  (1971-2000)', 'collections&url=shaft', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Shanghai Noon  (2000-2003)', 'collections&url=shanghainoon', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Sin City  (2005-2014)', 'collections&url=sincity', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Sinister  (2012-2015)', 'collections&url=sinister', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Sister Act  (1995-1993)', 'collections&url=sisteract', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Smokey and the Bandit  (1977-1986)', 'collections&url=smokeyandthebandit', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Speed  (1994-1997)', 'collections&url=speed', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Spider-Man  (2002-2017)', 'collections&url=spiderman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Stakeout  (1987-1993)', 'collections&url=stakeout', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Star Trek  (1979-2016)', 'collections&url=startrek', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Star Wars  (1977-2015)', 'collections&url=starwars', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Superman  (1978-2016)', 'collections&url=superman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Sting  (1973-1983)', 'collections&url=thesting', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Taken  (2008-2014)', 'collections&url=taken', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Taxi  (1998-2007)', 'collections&url=taxi', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Ted  (2012-2015)', 'collections&url=ted', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Teen Wolf  (1985-1987)', 'collections&url=teenwolf', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Terminator  (1984-2015)', 'collections&url=terminator', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Terms of Endearment  (1983-1996)', 'collections&url=termsofendearment', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Texas Chainsaw Massacre  (1974-2013)', 'collections&url=texaschainsawmassacre', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' The Thing  (1982-2011)', 'collections&url=thething', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Thomas Crown Affair  (1968-1999)', 'collections&url=thomascrownaffair', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Transporter  (2002-2015)', 'collections&url=transporter', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Under Siege  (1992-1995)', 'collections&url=undersiege', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Universal Soldier  (1992-2012)', 'collections&url=universalsoldier', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Wall Street  (1987-2010)', 'collections&url=wallstreet', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Waynes World  (1992-1993)', 'collections&url=waynesworld', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Weekend at Bernies  (1989-1993)', 'collections&url=weekendatbernies', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Whole Nine Yards  (2000-2004)', 'collections&url=wholenineyards', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' X-Files  (1998-2008)', 'collections&url=xfiles', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' X-Men  (2000-2016)', 'collections&url=xmen', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' xXx  (2002-2005)', 'collections&url=xxx', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Young Guns  (1988-1990)', 'collections&url=youngguns', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Zoolander  (2001-2016)', 'collections&url=zoolander', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(' Zorro  (1998-2005)', 'collections&url=zorro', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
	self.endDirectory()

# tmdb.movies().actorBoxset()
    def actorBoxset(self):
        self.addDirectoryItem('Adam Sandler', 'collections&url=adamsandler', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Alpacino',     'collections&url=alpacino', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Alan Rickman', 'collections&url=alanrickman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Anthony Hopkins', 'collections&url=anthonyhopkins', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Angelina Jolie', 'collections&url=angelinajolie', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Arnold Schwarzenegger', 'collections&url=arnoldschwarzenegger', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Charlize Theron', 'collections&url=charlizetheron', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Clint Eastwood', 'collections&url=clinteastwood', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Demi Moore', 'collections&url=demimoore', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Denzel Washington', 'collections&url=denzelwashington', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Eddie Murphy', 'collections&url=eddiemurphy', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Gene Wilder', 'collections&url=genewilder', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Gerard Butler', 'collections&url=gerardbutler', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Goldie Hawn', 'collections&url=goldiehawn', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Jason Statham', 'collections&url=jasonstatham', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Jean Claude Van Damme', 'collections&url=jeanclaudevandamme', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Jeffrey Dean Morgan', 'collections&url=jeffreydeanmorgan', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('John Travolta', 'collections&url=johntravolta', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Johnny Depp', 'collections&url=johnnydepp', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Julia Roberts', 'collections&url=juliaroberts', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Kevin Costner', 'collections&url=kevincostner', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Liam Neeson', 'collections&url=liamneeson', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Mel Gibson', 'collections&url=melgibson', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Melissa McCarthy', 'collections&url=melissamccarthy', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Meryl Streep', 'collections&url=merylstreep', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Michelle Pfeiffer', 'collections&url=michellepfeiffer', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Nicolas Cage', 'collections&url=nicolascage', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Nicole Kidman', 'collections&url=nicolekidman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Paul Newman', 'collections&url=paulnewman', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Reese Witherspoon', 'collections&url=reesewitherspoon', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Robert De Niro', 'collections&url=robertdeniro', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Samuel L Jackson', 'collections&url=samueljackson', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Sean connery', 'collections&url=seanconnery', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Scarlett Johansson', 'collections&url=scarlettjohansson', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Sharon Stone', 'collections&url=sharonstone', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Sigourney Weaver', 'collections&url=sigourneyweaver', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Steven Seagal', 'collections&url=stevenseagal', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Sylvester stallone', 'collections&url=Sylvesterstallone', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Vin Diesel', 'collections&url=vindiesel', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Wesley Snipes', 'collections&url=wesleysnipes', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Will Smith', 'collections&url=willsmith', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Winona Ryder', 'collections&url=winonaryder', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.endDirectory()


    def holidaysBoxset(self):
        self.addDirectoryItem('Christmas', 'collections&url=xmasmovies2', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Easter', 'collections&url=eastermovies', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Halloween', 'collections&url=halloweenmovies', 'tmdb2.png', 'DefaultRecentlyAddedMovies.png')
        self.endDirectory()
 

############################################################################################################################################################
    def tmdb_list(self, url):
        next = url
        try:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))
        except:
            pass
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['results']
        except:
            return
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total:
                raise Exception()
            url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            result = client.request(url2)
            result = json.loads(result)
            items += result['results']
        except:
            pass
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total:
                raise Exception()
            if not 'page=' in url:
                raise Exception()
            next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))
            next = next.encode('utf-8')
        except:
            next = ''
        for item in items:
            try:
                title = item['title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                year = item['release_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')
                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')
                poster = item['poster_path']
                if poster == '' or poster == None:
                    poster = '0'
                else:
                    poster = self.tmdb_poster + poster
                poster = poster.encode('utf-8')
                fanart = item['backdrop_path']
                if fanart == '' or fanart == None:
                    fanart = '0'
                if not fanart == '0':
                    fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')
                premiered = item['release_date']
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'
                premiered = premiered.encode('utf-8')
                rating = str(item['vote_average'])
                if rating == '' or rating == None:
                    rating = '0'
                rating = rating.encode('utf-8')
                votes = str(item['vote_count'])
                try:
                    votes = str(format(int(votes),',d'))
                except:
                    pass
                if votes == '' or votes == None:
                    votes = '0'
                votes = votes.encode('utf-8')
                plot = item['overview']
                if plot == '' or plot == None:
                    plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')
                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try:
                    tagline = tagline.encode('utf-8')
                except:
                    pass
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': tagline, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})
            except:
                pass
        return self.list


    def trakt_list(self, url):
        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
            result = trakt.getTraktAsJson(u)
            items = []
            for i in result:
                try:
                    items.append(i['movie'])
                except:
                    pass
            if len(items) == 0:
                items = result
        except:
            return
        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            p = str(int(q['page']) + 1)
            if p == '5':
                raise Exception()
            q.update({'page': p})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
            next = next.encode('utf-8')
        except:
            next = ''
        for item in items:
            try:
                title = item['title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                year = item['year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')
                if int(year) > int((self.datetime).strftime('%Y')):
                    raise Exception()
                tmdb = item['ids']['tmdb']
                if tmdb == None or tmdb == '':
                    tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')
                imdb = item['ids']['imdb']
                if imdb == None or imdb == '':
                    raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')
                poster = '0'
                try:
                    poster = item['images']['poster']['medium']
                except:
                    pass
                if poster == None or not '/posters/' in poster:
                    poster = '0'
                poster = poster.rsplit('?', 1)[0]
                poster = poster.encode('utf-8')
                banner = poster
                try:
                    banner = item['images']['banner']['full']
                except:
                    pass
                if banner == None or not '/banners/' in banner:
                    banner = '0'
                banner = banner.rsplit('?', 1)[0]
                banner = banner.encode('utf-8')
                fanart = '0'
                try:
                    fanart = item['images']['fanart']['full']
                except:
                    pass
                if fanart == None or not '/fanarts/' in fanart:
                    fanart = '0'
                fanart = fanart.rsplit('?', 1)[0]
                fanart = fanart.encode('utf-8')
                premiered = item['released']
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'
                premiered = premiered.encode('utf-8')
                genre = item['genres']
                genre = [i.title() for i in genre]
                if genre == []:
                    genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                try:
                    duration = str(item['runtime'])
                except:
                    duration = '0'
                if duration == None:
                    duration = '0'
                duration = duration.encode('utf-8')
                try:
                    rating = str(item['rating'])
                except:
                    rating = '0'
                if rating == None or rating == '0.0':
                    rating = '0'
                rating = rating.encode('utf-8')
                try:
                    votes = str(item['votes'])
                except:
                    votes = '0'
                try:
                    votes = str(format(int(votes),',d'))
                except:
                    pass
                if votes == None:
                    votes = '0'
                votes = votes.encode('utf-8')
                mpaa = item['certification']
                if mpaa == None:
                    mpaa = '0'
                mpaa = mpaa.encode('utf-8')
                plot = item['overview']
                if plot == None:
                    plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')
                try:
                    tagline = item['tagline']
                except:
                    tagline = None
                if tagline == None and not plot == '0':
                    tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                elif tagline == None:
                    tagline = '0'
                tagline = client.replaceHTMLCodes(tagline)
                try:
                    tagline = tagline.encode('utf-8')
                except:
                    pass
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': tagline, 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'banner': banner, 'fanart': fanart, 'next': next})
            except:
                pass
        return self.list


    def imdb_list(self, url):
        try:
            if url == self.imdbwatchlist_link:
                def imdb_watchlist_id(url):
                    return re.findall('/export[?]list_id=(ls\d*)', client.request(url))[0]
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url
            result = client.request(url)
            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'tr', attrs = {'class': '.+?'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return
        try:
            next = client.parseDOM(result, 'span', attrs = {'class': 'pagination'})
            next += client.parseDOM(result, 'div', attrs = {'class': 'pagination'})
            name = client.parseDOM(next[-1], 'a')[-1]
            if 'laquo' in name:
                raise Exception()
            next = client.parseDOM(next, 'a', ret='href')[-1]
            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''
        for item in items:
            try:
                try:
                    title = client.parseDOM(item, 'a')[1]
                except:
                    pass
                try:
                    title = client.parseDOM(item, 'a', attrs = {'onclick': '.+?'})[-1]
                except:
                    pass
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                year = client.parseDOM(item, 'span', attrs = {'class': 'year_type'})[0]
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')
                if int(year) > int((self.datetime).strftime('%Y')):
                    raise Exception()
                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = 'tt' + re.sub('[^0-9]', '', imdb.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')
                poster = '0'
                try:
                    poster = client.parseDOM(item, 'img', ret='src')[0]
                except:
                    pass
                try:
                    poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except:
                    pass
                if not ('_SX' in poster or '_SY' in poster):
                    poster = '0'
                poster = re.sub('_SX\d*|_SY\d*|_CR\d+?,\d+?,\d+?,\d*','_SX500', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')
                genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})
                genre = client.parseDOM(genre, 'a')
                genre = ' / '.join(genre)
                if genre == '':
                    genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')
                try:
                    duration = re.compile('(\d+?) mins').findall(item)[-1]
                except:
                    duration = '0'
                duration = client.replaceHTMLCodes(duration)
                duration = duration.encode('utf-8')
                try:
                    rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except:
                    rating = '0'
                try:
                    rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except:
                    rating = '0'
                if rating == '' or rating == '-':
                    rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')
                try:
                    votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': 'rating rating-list'})[0]
                except:
                    votes = '0'
                try:
                    votes = re.compile('[(](.+?) votes[)]').findall(votes)[0]
                except:
                    votes = '0'
                if votes == '':
                    votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')
                try:
                    mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except:
                    mpaa = '0'
                try:
                    mpaa = client.parseDOM(mpaa, 'span', ret='title')[0]
                except:
                    mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED':
                    mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')
                director = client.parseDOM(item, 'span', attrs = {'class': 'credit'})
                director += client.parseDOM(item, 'div', attrs = {'class': 'secondary'})
                try:
                    director = [i for i in director if 'Director:' in i or 'Dir:' in i][0]
                except:
                    director = '0'
                director = director.split('With:', 1)[0].strip()
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '':
                    director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')
                cast = client.parseDOM(item, 'span', attrs = {'class': 'credit'})
                cast += client.parseDOM(item, 'div', attrs = {'class': 'secondary'})
                try:
                    cast = [i for i in cast if 'With:' in i or 'Stars:' in i][0]
                except:
                    cast = '0'
                cast = cast.split('With:', 1)[-1].strip()
                cast = client.replaceHTMLCodes(cast)
                cast = cast.encode('utf-8')
                cast = client.parseDOM(cast, 'a')
                if cast == []:
                    cast = '0'
                plot = '0'
                try:
                    plot = client.parseDOM(item, 'span', attrs = {'class': 'outline'})[0]
                except:
                    pass
                try:
                    plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except:
                    pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                if plot == '':
                    plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')
                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try:
                    tagline = tagline.encode('utf-8')
                except:
                    pass
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': '0', 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': imdb, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'banner': '0', 'fanart': '0', 'next': next})
            except:
                pass
        return self.list


    def worker(self):
        self.meta = []
        total = len(self.list)
        for i in range(0, total):
            self.list[i].update({'metacache': False})
        self.list = metacache.fetch(self.list, self.tmdb_lang)
        for r in range(0, total, 100):
            threads = []
            for i in range(r, r+100):
                if i <= total:
                    threads.append(workers.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]
        self.list = [i for i in self.list]
        if len(self.meta) > 0:
            metacache.insert(self.meta)


    def super_info(self, i):
        try:
            if self.list[i]['metacache'] == True:
                raise Exception()
            try:
                tmdb = self.list[i]['tmdb']
            except:
                tmdb = '0'
            if not tmdb == '0':
                url = self.tmdb_info_link % tmdb
            else:
                raise Exception()
            item = client.request(url, timeout='10')
            item = json.loads(item)
            title = item['title']
            if not title == '0':
                self.list[i].update({'title': title})
            year = item['release_date']
            try:
                year = re.compile('(\d{4})').findall(year)[0]
            except:
                year = '0'
            if year == '' or year == None:
                year = '0'
            year = year.encode('utf-8')
            if not year == '0':
                self.list[i].update({'year': year})
            tmdb = item['id']
            if tmdb == '' or tmdb == None:
                tmdb = '0'
            tmdb = re.sub('[^0-9]', '', str(tmdb))
            tmdb = tmdb.encode('utf-8')
            if not tmdb == '0':
                self.list[i].update({'tmdb': tmdb})
            imdb = item['imdb_id']
            if imdb == '' or imdb == None:
                imdb = '0'
            imdb = imdb.encode('utf-8')
            if not imdb == '0' and "tt" in imdb:
                self.list[i].update({'imdb': imdb, 'code': imdb})
            poster = item['poster_path']
            if poster == '' or poster == None:
                poster = '0'
            if not poster == '0':
                poster = '%s%s' % (self.tmdb_poster, poster)
            poster = poster.encode('utf-8')
            if not poster == '0':
                self.list[i].update({'poster': poster})
            fanart = item['backdrop_path']
            if fanart == '' or fanart == None:
                fanart = '0'
            if not fanart == '0':
                fanart = '%s%s' % (self.tmdb_image, fanart)
            fanart = fanart.encode('utf-8')
            if not fanart == '0' and self.list[i]['fanart'] == '0':
                self.list[i].update({'fanart': fanart})
            premiered = item['release_date']
            try:
                premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
            except:
                premiered = '0'
            if premiered == '' or premiered == None:
                premiered = '0'
            premiered = premiered.encode('utf-8')
            if not premiered == '0':
                self.list[i].update({'premiered': premiered})
            studio = item['production_companies']
            try:
                studio = [x['name'] for x in studio][0]
            except:
                studio = '0'
            if studio == '' or studio == None:
                studio = '0'
            studio = studio.encode('utf-8')
            if not studio == '0':
                self.list[i].update({'studio': studio})
            genre = item['genres']
            try:
                genre = [x['name'] for x in genre]
            except:
                genre = '0'
            if genre == '' or genre == None or genre == []:
                genre = '0'
            genre = ' / '.join(genre)
            genre = genre.encode('utf-8')
            if not genre == '0':
                self.list[i].update({'genre': genre})
            try:
                duration = str(item['runtime'])
            except:
                duration = '0'
            if duration == '' or duration == None:
                duration = '0'
            duration = duration.encode('utf-8')
            if not duration == '0':
                self.list[i].update({'duration': duration})
            rating = str(item['vote_average'])
            if rating == '' or rating == None:
                rating = '0'
            rating = rating.encode('utf-8')
            if not rating == '0':
                self.list[i].update({'rating': rating})
            votes = str(item['vote_count'])
            try:
                votes = str(format(int(votes),',d'))
            except:
                pass
            if votes == '' or votes == None:
                votes = '0'
            votes = votes.encode('utf-8')
            if not votes == '0':
                self.list[i].update({'votes': votes})
            mpaa = item['releases']['countries']
            try:
                mpaa = [x for x in mpaa if not x['certification'] == '']
            except:
                mpaa = '0'
            try:
                mpaa = ([x for x in mpaa if x['iso_3166_1'].encode('utf-8') == 'US'] + [x for x in mpaa if not x['iso_3166_1'].encode('utf-8') == 'US'])[0]['certification']
            except:
                mpaa = '0'
            mpaa = mpaa.encode('utf-8')
            if not mpaa == '0':
                self.list[i].update({'mpaa': mpaa})
            director = item['credits']['crew']
            try:
                director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
            except:
                director = '0'
            if director == '' or director == None or director == []:
                director = '0'
            director = ' / '.join(director)
            director = director.encode('utf-8')
            if not director == '0':
                self.list[i].update({'director': director})
            writer = item['credits']['crew']
            try:
                writer = [x['name'] for x in writer if x['job'].encode('utf-8') in ['Writer', 'Screenplay']]
            except:
                writer = '0'
            try:
                writer = [x for n,x in enumerate(writer) if x not in writer[:n]]
            except:
                writer = '0'
            if writer == '' or writer == None or writer == []:
                writer = '0'
            writer = ' / '.join(writer)
            writer = writer.encode('utf-8')
            if not writer == '0':
                self.list[i].update({'writer': writer})
            cast = item['credits']['cast']
            try:
                cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
            except:
                cast = []
            if len(cast) > 0:
                self.list[i].update({'cast': cast})
            plot = item['overview']
            if plot == '' or plot == None:
                plot = '0'
            plot = plot.encode('utf-8')
            if not plot == '0':
                self.list[i].update({'plot': plot})
            tagline = item['tagline']
            if (tagline == '' or tagline == None) and not plot == '0':
                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
            elif tagline == '' or tagline == None:
                tagline = '0'
            try:
                tagline = tagline.encode('utf-8')
            except:
                pass
            if not tagline == '0':
                self.list[i].update({'tagline': tagline})
            try:
                if not imdb == None or imdb == '0':
                    url = self.imdbinfo % imdb
                    item = client.request(url, timeout='10')
                    item = json.loads(item)
                    plot2 = item['Plot']
                    if plot2 == '' or plot2 == None:
                        plot = plot
                    plot = plot.encode('utf-8')
                    if not plot == '0':
                        self.list[i].update({'plot': plot})
                    rating2 = str(item['imdbRating'])
                    if rating2 == '' or rating2 == None:
                        rating = rating2
                    rating = rating.encode('utf-8')
                    if not rating == '0':
                        self.list[i].update({'rating': rating})
                    votes2 = str(item['imdbVotes'])
                    try:
                        votes2 = str(votes2)
                    except:
                        pass
                    if votes2 == '' or votes2 == None:
                        votes = votes2
                    votes = votes.encode('utf-8')
                    if not votes == '0':
                        self.list[i].update({'votes': votes2})
            except:
                pass
            self.meta.append({'tmdb': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.tmdb_lang, 'item': {'title': title, 'year': year, 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster, 'fanart': fanart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline}})
        except:
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0:
            control.idle(); sys.exit()
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')
        traktCredentials = trakt.getTraktCredentialsInfo()
        try:
            isOld = False; control.item().getArt('type')
        except:
            isOld = True
        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'
        indicators = playcount.getMovieIndicators(refresh=True) if action == 'movies' else playcount.getMovieIndicators()
        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')
        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')
        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')
        queueMenu = control.lang(32065).encode('utf-8')
        traktManagerMenu = control.lang(32070).encode('utf-8')
        nextMenu = control.lang(32053).encode('utf-8')
        addToLibrary = control.lang(32551).encode('utf-8')
        for i in items:
            try:
                label = '%s (%s)' % (i['title'], i['year'])
                imdb, tmdb, title, year = i['imdb'], i['tmdb'], i['originaltitle'], i['year']
                sysname = urllib.quote_plus('%s (%s)' % (title, year))
                systitle = urllib.quote_plus(title)
                meta = dict((k, v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tmdb_id': tmdb})
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not 'duration' in i:
                    meta.update({'duration': '120'})
                elif i['duration'] == '0':
                    meta.update({'duration': '120'})
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                try:
                    meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except:
                    pass
                poster = [i[x] for x in ['poster', 'poster2', 'poster3'] if i.get(x, '0') != '0']
                poster = poster[0] if poster else addonPoster
                meta.update({'poster': poster})
                sysmeta = urllib.quote_plus(json.dumps(meta))
                url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)
                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)
                cm = []
                cm.append(('Find similar', 'ActivateWindow(10025,%s?action=movies&url=https://api.trakt.tv/movies/%s/related,return)' % (sysaddon, imdb)))
                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (sysaddon, sysname, imdb)))
                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))
                cm.append((addToLibrary, 'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))
                item = control.item(label=label)
                art = {}
                art.update({'icon': poster, 'thumb': poster, 'poster': poster})
                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                else:
                    art.update({'banner': addonBanner})
                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})
                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})
                if settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                    item.setProperty('Fanart_Image', i['fanart2'])
                elif settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)
                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
                item.setInfo(type='Video', infoLabels = control.metadataClean(meta))
                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass
        try:
            url = items[0]['next']
            if url == '':
                raise Exception()
            icon = control.addonNext()
            url = '%s?action=moviePage&url=%s' % (sysaddon, urllib.quote_plus(url))
            item = control.item(label=nextMenu)
            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None:
                item.setProperty('Fanart_Image', addonFanart)
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass
        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})



    def addDirectoryItem(self, name, query, thumb, icon, queue=False, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        thumb = os.path.join(artPath, thumb) if not artPath == None else icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self):
        control.directory(syshandle, cacheToDisc=True)




