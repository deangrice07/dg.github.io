# -*- coding: utf-8 -*-
############################################################################################################################################################################                                                                                                                                       #                                                                                                                                                                          #
#                                                                                                                                                                          #
#    ##     .   **       #########.  ########   #########   ##     ##    #########   #########   #########   #########   #########   ########   #########   ##########     #
#    ##         ##       ##     ##     ###      ##     ##   ###    ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ##     ##     ###      ##     ##   ## #   ##    ##          ##          ##     ##   ##     ##   ##     ##   ##         ##     ##   ##             #
#    ##         ##       ########      ###      ##     ##   ##  #  ##    #########   ##          ########    #########   ## ######   ########   ########    ##########     #
#    ##         ##       ##            ###      ##     ##   ##   # ##           ##   ##          ##    ##    ##     ##   ##          ##         ##    ##            ##     #
#    ##         ##       ##            ###      ##     ##   ##    ###           ##   ##          ##     ##   ##     ##   ##          ##         ##     ##           ##     #
#    #######    ##       ##     .      ###      #########   ##     ##    #########   ##########  ##      #   ##     ##   ##          ########   ##      #   ##########     #
############################################################################################################################################################################
# learn to understand scrapers #
################################
# Testing @Cy4Root 01-10-2019 movie:  First Blood (1982)
 
import re
import requests
from collections import deque
from urllib import quote_plus
from time import time, sleep as timeSleep
from bs4 import BeautifulSoup, SoupStrainer

from liptonscrapers.modules.client import randomagent


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviesjoy.net']

        self.BASE_URL = 'https://www.moviesjoy.net'
        self.QUICK_SEARCH_PATH = '/ajax/movie_suggest_search'
        self.SERVER_PATH = '/ajax/v4_movie_episodes/%s/%s'
        self.EMBED_PATH = '/ajax/movie_embed/'
        self.DIRECT_PATH = '/ajax/movie_sources/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return self._getSearchData(title, aliases, year, self._createSession(), season=None, episode=None)
        except:
            self._logException()
            return None


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return tvshowtitle, aliases, year
        except:
            self._logException()
            return None


    def episode(self, data, imdb, tvdb, title, premiered, season, episode):
        try:
            tvshowtitle, aliases, year = data
            return self._getSearchData(tvshowtitle, aliases, year, self._createSession(), season, episode)
        except:
            self._logException()
            return None


    def sources(self, data, hostDict, hostprDict):
        try:
            session = self._createSession(data)
            r = self._sessionRequest(data['url'], session, 1.5)
            if not r.ok:
                self._logException('Sources page request #1 failed: ' + data['url'])
                return None

            # Extract some values we need from the HTML.
            htmlContent = r.content
            dataIndex = htmlContent.rfind(b'var movie =')
            id, movie_id = re.search(
                b"""id.*?['"](.*?)['"].*?movie_id.*?['"](.*?)['"]""",
                htmlContent[dataIndex : dataIndex+200],
                re.DOTALL
            ).groups()

            session.cookies['view-' + str(id)] = 'true' # A cookie that they use.
            session.headers['Referer'] = data['url'].replace('.html', '/watching.html')

            r = self._sessionRequest(
                self.BASE_URL + (self.SERVER_PATH % (id, movie_id)),
                session,
                0.7,
                data = None,
                ajax = True
            )
            if not r.ok:
                self._logException('Sources page request #2 failed: ' + data['url'])
                return None

            userAgent = data['UA']
            referer = session.headers['Referer']
            cookies = session.cookies.get_dict()

            # Prepare some Kodi headers for direct sources, if any.
            directHeaders = '|User-Agent=' + quote_plus(userAgent) + '&Referer=' + quote_plus(referer)

            divs = BeautifulSoup(r.json()['html'], 'html.parser', parse_only=SoupStrainer('div'))

            def _sourcesGen():
                if data['episode'] != None:
                    isEpisode = True
                    episode = int(data['episode'])
                    episodeRE = re.compile('''(\d+)''')
                else:
                    isEpisode = False

                for div in divs:
                    if isEpisode:
                        # TV episode sources.
                        # Episodes are <li> tags ordered from newest to oldest inside the <div> of a server.
                        for li in div.find_all('li'):
                            match = episodeRE.search(li.a.string.lower())
                            if match and int(match.group(1)) == episode:
                                break # We found the episode <li> we're looking for.
                        else:
                            continue # No matching episode found in this server <div>.
                    else:
                        # Movie sources, only one <li>.
                        li = div.li

                    resolveData = {
                        'data-id': li['data-id'],
                        'data-server': li['data-server'],
                        'UA': userAgent,
                        'referer': referer,
                        'cookies': cookies
                    }

                    if 'direct' in li['onclick']:
                        # Resolve a direct source right now. There's usually only one anyway, Alphabet (Google Video).
                        r = self._sessionRequest(
                            self.BASE_URL + (self.DIRECT_PATH + li['data-id'] + '-' + li['data-server']),
                            session,
                            delayAmount = 1.0,
                            data = None,
                            ajax = True
                        )
                        hostName = div.span.text
                        # Multiple qualities in the direct source.
                        for quality in r.json()['playlist'][0]['sources']:
                            yield {
                                'source': hostName,
                                'quality': quality['label'],
                                'language': 'en',
                                'url': quality['file'] + directHeaders,
                                'direct': True,
                                'debridonly': False
                            }
                    else:
                        yield {
                            'source': div.span.text,
                            'quality': 'SD',
                            'language': 'en',
                            'url': {
                                'data-id': li['data-id'],
                                'data-server': li['data-server'],
                                'UA': userAgent,
                                'referer': referer,
                                'cookies': cookies
                            },
                            'direct': False,
                            'debridonly': False
                        }

            return list(_sourcesGen())
        except:
            self._logException()
            return None


    def resolve(self, data):
        if not isinstance(data, dict):
            return data # Already resolved.

        # Ask the website for the embed URL.
        session = self._createSession(data)
        r = self._sessionRequest(
            self.BASE_URL + (self.EMBED_PATH + data['data-id'] + '-' + data['data-server']),
            session,
            delayAmount = 1.2,
            data = None,
            ajax = True
        )
        if not r.ok:
            #self._logException('Resolve request failed: id=%s server=%s' % (data['data-id'], data['data-server']))
            return None
        return r.json().get('src', None)


    def _sessionRequest(self, url, session, delayAmount, data=None, ajax=None):
        try:
            startTime = time() if delayAmount else None

            if ajax:
                oldAccept = session.headers['Accept']
                session.headers.update(
                    {'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest'}
                )

            if data:
                r = session.post(url, data=data, timeout=8)
            else:
                r = session.get(url, timeout=8)

            if ajax:
                # Restore the session headers.
                session.headers['Accept'] = oldAccept
                del session.headers['X-Requested-With']

            if delayAmount:
                elapsed = time() - startTime
                if elapsed < delayAmount and elapsed > 0.1:
                    timeSleep(delayAmount - elapsed)
            return r
        except:
            return type('FailedResponse', (object,), {'ok': False})


    def _createSession(self, customHeaders={}):
        # Create a 'requests.Session' and try to spoof the headers from a desktop browser.
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': customHeaders['UA'] if 'UA' in customHeaders else randomagent(),
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': customHeaders['referer'] if 'referer' in customHeaders else self.BASE_URL + '/',
                'DNT': '1'
            }
        )
        if 'cookies' in customHeaders:
            session.cookies.update(customHeaders['cookies'])

        return session


    def _getSearchData(self, title, aliases, year, session, season, episode):
        try:
            query = quote_plus(title.lower().replace("'", ''))
            r = self._sessionRequest(
                self.BASE_URL + self.QUICK_SEARCH_PATH, session, 1.2, {'keyword': query}, ajax=True
            )
            if not r.ok:
                return None

            possibleTitles = set(
                (title.lower(),) + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )

            # Using the pop-up search results uses way less bandwidth from them, like 1 KB (instead of 9 KB with
            # the traditional search page).

            bestURL = None

            allAs = BeautifulSoup(r.json()['content'], 'html.parser', parse_only=SoupStrainer('a', href=True))
            if episode:
                # TV Show.
                for a in allAs:
                    if a.h3:
                        cleanH3 = a.h3.text.lower().replace('&lt;', '<').replace('&gt;', '>')
                        entryText, entrySeason = re.search('(.*?)(?: - season ([\d]*))?\Z', cleanH3).groups()
                        if entryText in possibleTitles and entrySeason in season:
                            bestURL = a['href']
                            break
            else:
                # Movie / non-episodic content.
                bestURLs = [ ]
                for a in allAs:
                    if a.h3:
                        cleanH3 = a.h3.text.lower().replace('&lt;', '<').replace('&gt;', '>')
                        if cleanH3 in possibleTitles:
                            if a.span.text == year:
                                bestURLs.insert(0, a['href']) # Give higher priority when the year is also matched.
                            else:
                                bestURLs.append(a['href'])
                bestURL = bestURLs[0] if bestURLs else None

            if bestURL:
                return {
                    'url': bestURL,
                    'episode': episode,
                    'UA': session.headers['User-Agent'],
                    'referer': self.BASE_URL + '/',
                    'cookies': session.cookies.get_dict()
                }
            else:
                return None # No results found.
        except:
            self._logException()
            return None


    def _debug(self, name, val=None):
        import xbmc
        xbmc.log(
            'MOVIESJOY-NET Debug > %s %s' % (name, (val if isinstance(val, str) else (repr(val) if val else ''))),
            xbmc.LOGWARNING
        )


    def _logException(self, text=None):
        return # Comment this return statement to output errors to the Kodi log, useful for debugging this script.
        import xbmc
        if text:
            xbmc.log('MOVIESJOY-NET Error >' + text, xbmc.LOGERROR)
        else:
            import traceback
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
