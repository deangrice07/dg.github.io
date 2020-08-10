
import requests, json, re, time,logging,sys,xbmcgui,xbmc,os

from resources.modules.general import base_header
import subprocess
import xbmcaddon
Addon = xbmcaddon.Addon()
try:
    resuaddon=xbmcaddon.Addon('script.module.resolveurl')
except Exception as e:
    pass
def copy2clip(txt):
    platform = sys.platform

    if platform == 'win32':
        try:
            cmd = 'echo ' + txt.strip() + '|clip'
            return subprocess.check_call(cmd, shell=True)
            pass
        except:
            pass
    elif platform == 'linux2':
        try:
            from subprocess import Popen, PIPE

            p = Popen(['xsel', '-pi'], stdin=PIPE)
            p.communicate(input=txt)
        except:
            pass
    else:
        pass
    pass
def colorString(text, color=None):
    try:
        text = text.encode('utf-8')
    except:
        try:
            text = bytes(text).decode('utf-8')
            text = str(text)
        except:
            pass
        pass

    if color is 'default' or color is '' or color is None:
        color = ''
        if color is '':
            color = 'deepskyblue'

    try:
        return '[COLOR ' + str(color) + ']' + text + '[/COLOR]'
    except:
        return '[COLOR ' + str(color) + ']' + text   + '[/COLOR]'
class RealDebrid:

    def __init__(self):
        self.count_rd=0
        self.ClientID = Addon.getSetting('rd.client_id')
        if self.ClientID == '':
            self.ClientID = 'X245A4XAIBGVM'
        self.OauthUrl = 'https://api.real-debrid.com/oauth/v2/'
        self.DeviceCodeUrl = "device/code?%s"
        self.DeviceCredUrl = "device/credentials?%s"
        self.TokenUrl = "token"
        self.token = Addon.getSetting('rd.auth')
        self.ClientSecret = Addon.getSetting('rd.secret')
        if self.ClientSecret=='':
            self.auth()
        self.refresh = Addon.getSetting('rd.refresh')
        self.DeviceCode = ''
        
        self.OauthTimeout = 0
        self.OauthTimeStep = 0
        self.BaseUrl = "https://api.real-debrid.com/rest/1.0/"

    def auth_loop(self,dp):

        if dp.iscanceled():
            dp.close()
            return
        
        time.sleep(self.OauthTimeStep)
        url = "client_id=%s&code=%s" % (self.ClientID, self.DeviceCode)
        url = self.OauthUrl + self.DeviceCredUrl % url
  
        response = json.loads(requests.get(url).text)

        error=response.get("error","OK")
        if error==1 or 'client_id' not in response:
            
            return
        else:
            dp.close()
            
            Addon.setSetting('rd.client_id', response['client_id'])
            Addon.setSetting('rd.secret', response['client_secret'])
            try:
                resuaddon.setSetting('RealDebridResolver_client_id', response['client_id'])
                resuaddon.setSetting('RealDebridResolver_client_secret', response['client_secret'])
            except:
                pass
            self.ClientSecret = response['client_secret']
            self.ClientID = response['client_id']
            logging.warning('All Good')
            return
    def list_torrents(self):
        url = "torrents"
        response = self.get_url(url)
        return response
        
    def get_history(self,page):
        
        
        return self.get_url("downloads?page=" + page)
    def auto_auth(self,code,o_response):
        import requests,time
        username=Addon.getSetting("rd_user")
        password=Addon.getSetting("rd_pass")
        import datetime
        dp = xbmcgui . DialogProgress ( )
        dp.create("Real Debrid Auth",Addon.getLocalizedString(32072), Addon.getLocalizedString(32274))
        dp.update(0, "Real Debrid Auth", Addon.getLocalizedString(32276))
        
        now=int(time.mktime(datetime.datetime.now().timetuple())) * 1000
        cookies = {
            'https': '1',
            'lang': 'en',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://real-debrid.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        params = (
            ('user', username),
            ('pass', password),
            ('pin_challenge', ''),
            ('pin_answer', 'PIN: 000000'),
            ('time', now),
                     
        )

        response = requests.get('https://real-debrid.com/ajax/login.php', headers=headers, params=params, cookies=cookies).json()
        if response['error']==1:
            xbmcgui.Dialog().ok('Error', response['message'])
            return 'bad'
        if response['captcha']==1:
            xbmcgui.Dialog().ok('Error', 'Error in Auto connection')
            return 'bad'
        dp.update(int(30), Addon.getLocalizedString(32072),Addon.getLocalizedString(32258), 'Ok' )

        cookies = {
            'https': '1',
            'lang': 'en',
            'auth': response['cookie'].split('=')[1],
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://real-debrid.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        data = {
          'usercode': code,
          'action': 'Continue'
        }
        
        response2 = requests.post('https://real-debrid.com/device', headers=headers, cookies=cookies, data=data)
        dp.update(int(60), Addon.getLocalizedString(32072),Addon.getLocalizedString(32298)+code, 'Ok' )
        cookies = {
            'https': '1',
            'lang': 'en',
            'auth': response['cookie'].split('=')[1],
            'language': 'en_GB',
            'amazon-pay-connectedAuth': 'connectedAuth_general',
            'session-set': 'true',
            'amazon-pay-abtesting-new-widgets': 'true',
            'amazon-pay-abtesting-apa-migration': 'true',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://real-debrid.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

        params = (
            ('client_id', self.ClientID),
            ('device_id', o_response['device_code']),
        )

        data = {
          'action': 'Allow'
        }

        response = requests.post('https://real-debrid.com/authorize', headers=headers, params=params, cookies=cookies, data=data)

        dp.update(int(90), Addon.getLocalizedString(32072),Addon.getLocalizedString(32079), 'Ok' )
       
        self.OauthTimeout = int(o_response['expires_in'])
        self.OauthTimeStep = int(o_response['interval'])
        self.DeviceCode = o_response['device_code']
        counter=0
        while self.ClientSecret == '':
            dp.update(int(100), Addon.getLocalizedString(32072),Addon.getLocalizedString(32080), str(counter) )
            self.auth_loop(dp)
            
            counter+=1
            if dp.iscanceled():
              dp.close()
              return 0
            xbmc.sleep(100)
 
        self.token_request()
        
        xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32081))).encode('utf-8'))
        return 'ok'
    def auth(self):

        self.ClientSecret = ''
        self.ClientID = 'X245A4XAIBGVM'
        url = ("client_id=%s&new_credentials=yes" % self.ClientID)
        url = self.OauthUrl + self.DeviceCodeUrl % url
     
        response = json.loads(requests.get(url).text)

        if 1:
            copy2clip(response['user_code'])

        
            dp = xbmcgui . DialogProgress ( )
            dp.create("Real Debrid "+Addon.getLocalizedString(32282),Addon.getLocalizedString(32283) + ' %s' % colorString('https://real-debrid.com/device'), Addon.getLocalizedString(32284)  + ' %s' % colorString(response['user_code']), Addon.getLocalizedString(32285))
            dp.update(-1, Addon.getLocalizedString(32283) + ' %s' % colorString('https://real-debrid.com/device'), Addon.getLocalizedString(32284) + ' %s' % colorString(response['user_code']), Addon.getLocalizedString(32285))
            
        
            self.OauthTimeout = int(response['expires_in'])
            self.OauthTimeStep = int(response['interval'])
            self.DeviceCode = response['device_code']
            while self.ClientSecret == '':
                self.auth_loop(dp)
                if dp.iscanceled():
                  dp.close()
                  return 0
                xbmc.sleep(300)
                
            self.token_request()

            return 0
    def token_request(self):
        import time

        if self.ClientSecret is '':
            return

        postData = {'client_id': self.ClientID,
                    'client_secret': self.ClientSecret,
                    'code': self.DeviceCode,
                    'grant_type': 'http://oauth.net/grant_type/device/1.0'}

        url = self.OauthUrl + self.TokenUrl
        response = requests.post(url, data=postData).text

        response = json.loads(response)
 
        Addon.setSetting('rd.auth', response['access_token'])
        Addon.setSetting('rd.refresh', response['refresh_token'])
        try:
            resuaddon.setSetting('RealDebridResolver_token', response['access_token'])
            resuaddon.setSetting('RealDebridResolver_refresh', response['refresh_token'])
        except:
            pass
        self.token = response['access_token']
        self.refresh = response['refresh_token']

        Addon.setSetting('rd.expiry', str(time.time() + int(response['expires_in'])))

       
   

    def refreshToken(self):
        import time
        postData = {'grant_type': 'http://oauth.net/grant_type/device/1.0',
                    'code': self.refresh,
                    'client_secret': self.ClientSecret,
                    'client_id': self.ClientID
                    }
        url = self.OauthUrl + 'token'
        response = requests.post(url, data=postData)
        #response =self.post_url(url, postData=postData)
        response = json.loads(response.text)

        try:
            if 'access_token' not in response:
                if 'error' in response:
                    added=str(response['error'])
                else:
                    added=''
                xbmcgui.Dialog().ok(Addon.getAddonInfo('name'), Addon.getLocalizedString(32286)+', [B]'+added+'[/B]')
        except:
            pass
        self.token = response['access_token']
        self.refresh = response['refresh_token']
        Addon.setSetting('rd.auth', self.token)
        Addon.setSetting('rd.refresh', self.refresh)
        Addon.setSetting('rd.expiry', str(time.time() + int(response['expires_in'])))
 
        ###############################################
        # To be FINISHED FINISH ME
        ###############################################
    def check_link(self,media_id):
        
        unrestrict_link_path = 'unrestrict/check'
        url =  ( unrestrict_link_path)
        postData = {'link': media_id}
        result = self.post_url(url, postData)
        return result
    def get_link(self,media_id):
        
        unrestrict_link_path = 'unrestrict/link'
        url =  ( unrestrict_link_path)
        postData = {'link': media_id}
        result = self.post_url(url, postData)
        return result
    def post_url(self, url, postData, fail_check=False):
        original_url = url
        url = self.BaseUrl + url
        if not fail_check:
            if '?' not in url:
                url += "?auth_token=%s" % self.token
            else:
                url += "&auth_token=%s" % self.token

        response = requests.post(url, data=postData).text
        try:
           jresonce= json.loads(response)
        except:
            jresonce=False
        if jresonce:
         if 'error' in jresonce:
          if 'bad_token' in jresonce['error'] or 'Bad Request' in jresonce['error']:
 
            
            if not fail_check:
                self.count_rd+=1
                
                if self.count_rd>4:
                    xbmcgui.Dialog().ok('Error', 'Error in RD comm')
                    sys.exit()
                self.refreshToken()
                response = self.post_url(original_url,postData, fail_check=False)
        try:
            return json.loads(response)
        except:
            return response
    def get_url_new1(self, url,data, fail_check=False):
        original_url = url
        url = self.BaseUrl + url
        url += "?auth_token=%s" % self.token

        response = requests.get(url,data=data).text
    
     
        try:
           return json.loads(response)
        except:
            return response
    def get_url_new(self, url,data, fail_check=False):
        original_url = url
        url = self.BaseUrl + url
        url += "?auth_token=%s" % self.token

        response = requests.put(url,data=data).text
    
     
        try:
           return json.loads(response)
        except:
            return response
    def get_url(self, url, fail_check=False):

        original_url = url
        url = self.BaseUrl + url
        if not fail_check:
            
            if '?' not in url:
                url += "?auth_token=%s" % self.token
            else:
                url += "&auth_token=%s" % self.token
        a=time.time()
        logging.warning('Send req time:'+str(a))
       
        response = requests.get(url,headers=base_header).content
        logging.warning('Got req time:'+str(a))
        try:
           jresonce= json.loads(response)
           logging.warning('Got response ok')
        except:
            jresonce=False
        if jresonce:
          if 'error' in jresonce:
            
            logging.warning(jresonce)
            if 'bad_token' in jresonce['error'] or 'Bad Request' in jresonce['error']:
   
               
                if not fail_check:
                    self.count_rd+=1
                    if self.count_rd>4:
                        xbmcgui.Dialog().ok('Error', 'Error in  RD')
                        sys.exit()
                    self.refreshToken()
                    response = self.get_url(original_url, fail_check=False)
        try:
           return json.loads(response)
        except:
            return response

    def checkHash(self, hashList):
        logging.warning('making hash list')
        hashString = ''
        if isinstance(hashList, list):
            for i in hashList:
                hashString += '/%s' % i
        else:
            hashString = "/" + hashList
        logging.warning('Sending hash list')
        return self.get_url("torrents/instantAvailability" + hashString)

    def addMagnet(self, magnet):
        postData = {'magnet': magnet}
        url = 'torrents/addMagnet'
        response = self.post_url(url, postData)
        return response

    def list_torrents(self):
        url = "torrents"
        response = self.get_url(url)
        return response

    def torrentInfo(self, id):
        url = "torrents/info/%s" % id
        return self.get_url(url)

    def torrentSelect(self, torrentID, fileID):
        url = "torrents/selectFiles/%s" % torrentID
        postData = {'files': fileID}
        return self.post_url(url, postData)

    def unrestrict_link(self, link):
        url = 'unrestrict/link'
        postData = {'link': link}
        response = self.post_url(url, postData)
        try:
            return response['download']
        except:
            return None
    def select_torrent_files(self,torrent_id, file_ids):
        uri = 'torrents/selectFiles/' + torrent_id
        if type(file_ids) is list:
            files = ','.join(file_ids)
        else:
            files = file_ids
        #RD.request(uri, data={"files": str(files)}, auth=True, encode_data=False)

        return self.post_url(uri, {"files": str(files['id'])})
       
    def deleteTorrent(self, id):
        url = "torrents/delete/%s&auth_token=%s" % (id, self.token)
        response = requests.delete(self.BaseUrl + url)
        
        
    def remove_history(self, id):
        url = "downloads/delete/%s&auth_token=%s" % (id, self.token)
        response = requests.delete(self.BaseUrl + url)
       
    def addtorrent(self,url):
        uri = 'torrents/addTorrent'
        file = open(url, 'rb') 
        dp = xbmcgui . DialogProgress ( )
        dp.create("Real Debrid","Starting", "", '')
        
    
        torrent=(self.get_url_new(uri,file))

       
        
        if 'id' in torrent:#try:
            res = self.torrentInfo(torrent['id'])
     
            if res['status']=='waiting_files_selection':
                   
                    fileIDString = ''
                    
                
                    if len(res['files'])>0:
                        max_size=0
                        for items in res['files']:
                            if items['bytes']>max_size:
                                max_size=items['bytes']
                                f_id=items['id']
                        start_file=f_id
                        
                       
                        self.torrentSelect(torrent['id'], start_file)#go
            f_size=0
            size=0
            status=''
            while status!='downloaded':
               
                status=res['status']
                size=res['bytes']
                unit=''
                unit2=''
                f_size=0
                f_size2=0
                if size>1024:
                    f_size=float(size)/1024
                    unit='Kb'
                if size>(1024*1024):
                    f_size=float(size)/(1024*1024)
                    unit='Mb'
                if size>(1024*1024*1024):
                    f_size=float(size)/(1024*1024*1024)
                    unit='Gb'
                size2=res['original_bytes']
                if size2>1024:
                    f_size2=float(size2)/1024
                    unit2='Kb'
                if size2>(1024*1024):
                    f_size2=float(size2)/(1024*1024)
                    unit2='Mb'
                if size2>(1024*1024*1024):
                    f_size2=float(size2)/(1024*1024*1024)
                    unit2='Gb'
                seed=''
                if 'seeders' in res:
                
                    seed='S-'+str(res['seeders'])
                if 'speed' in res:
                    unit3='b/s'
                    f_size3=res['speed']
                    if res['speed']>1024:
                        f_size3=float(res['speed'])/1024
                        unit3='Kb/s'
                    if res['speed']>(1024*1024):
                        f_size3=float(res['speed'])/(1024*1024)
                        unit3='Mb/s'
                    if res['speed']>(1024*1024*1024):
                        f_size3=float(res['speed'])/(1024*1024*1024)
                        unit3='Gb/s'
                    
                    speed=str(round(f_size3,2))+unit3
                else:
                    speed=''
                prog=0
                if 'progress' in res:
                    prog=res['progress']
                dp.update(prog, res['status']+' [COLOR yellow]'+seed+' '+speed+'[/COLOR]', res['original_filename'], str(round(f_size,2))+' '+unit+'/'+str(round(f_size2,2))+' '+unit2)
                xbmc.sleep(1000)
                res= requests.get(torrent['uri']+ "?auth_token=%s" % self.token).json()
                
            link = self.torrentInfo(torrent['id'])
            

            link = self.unrestrict_link(link['links'][0])
            
            
            self.deleteTorrent(torrent['id'])
            dp.close()
       
        
        #except:
        #    self.deleteTorrent(torrent['id'])
        #    return None
        
        return link
    def stop_play(self):
        KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('.', 1)[0])
        if KODI_VERSION>17:
            return 'forceexit'
        else:
            return 'return'
    def singleMagnetToLink(self, magnet):

        try:
            dp = xbmcgui . DialogProgress ( )
            dp.create("Real Debrid",Addon.getLocalizedString(32287), "", '')
            
            
            if self.ClientSecret == '':
                self.auth()
            '''
            hash = str(re.findall(r'btih:(.*?)&', magnet)[0].lower())
            hashCheck = self.checkHash(hash)
            fileIDString = ''

            if hash in hashCheck:
                
                if 'rd' in hashCheck[hash]:
                    if len(hashCheck[hash]['rd'])>0:
                        for key in hashCheck[hash]['rd'][0]:
                            fileIDString += ',' + key
            '''
            torrent = self.addMagnet(magnet)
            '''
            if 'uri' not in torrent:
                xbmcgui.Dialog().ok("error in RD",torrent)
                s=self.stop_play()
                if s=='forceexit':
                    sys.exit(1)
                else:
                    return 0
            '''
            dp.create("Real Debrid",Addon.getLocalizedString(32288), "", '')
            if dp.iscanceled():
                    self.deleteTorrent(torrent['id'])
                    dp.close()
                    return 'stop'
            res= requests.get(torrent['uri']+ "?auth_token=%s" % self.token).json()
            dp.create("Real Debrid","Got Answer", "", '')
            jump=False
            if res['status']=='waiting_files_selection':
                   
                fileIDString = ''
                
                f_id=''
                if len(res['files'])>0:
                    max_size=0
                    for items in res['files']:
                        if items['bytes']>max_size:
                            max_size=items['bytes']
                            if 'id' in items:
                                f_id=items['id']
                    start_file=f_id
                    
                    if f_id=='':
                      xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32288))).encode('utf-8'))
                    if 'id' in torrent:
                    
                        #self.torrentSelect(torrent['id'], start_file)#go
                        jump=True
                            
            f_size=0
            size=0
            status=''
            
             
            
            try:
                dp.create("Real Debrid",Addon.getLocalizedString(32290), "", '')
                link = self.torrentSelect(torrent['id'], start_file)
                dp.create("Real Debrid",Addon.getLocalizedString(32291), "", '')
                link = self.torrentInfo(torrent['id'])
                dp.create("Real Debrid",Addon.getLocalizedString(32292), "", '')
                link = self.unrestrict_link(link['links'][0])
                dp.create("Real Debrid",Addon.getLocalizedString(32293), "", '')
                self.deleteTorrent(torrent['id'])
            except:
                xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32289))).encode('utf-8'))
                if 'id' in torrent:
                    self.deleteTorrent(torrent['id'])
                return None
            dp.close()
            return link
      
        except Exception as e:
            if 'id' in torrent:
                self.deleteTorrent(torrent['id'])
            import linecache
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            if 'error' in torrent:
                if 'permission_denied' in torrent['error']:
                    error_n=torrent['error']+'\n Try reauth. debrid or check subscription'
                xbmcgui.Dialog().ok("error in RD",error_n)
                
            logging.warning(torrent)
            line = linecache.getline(filename, lineno, f.f_globals)
            #xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), 'Line:'+str(lineno)+' E:'+str(e))).encode('utf-8'))
            logging.warning('ERROR IN RD torrent :'+str(lineno))
            logging.warning('inline:'+line)
            logging.warning(e)
            logging.warning(torrent)
            logging.warning('BAD RD torrent')
            dp.close()
            try:
                if 'id' in torrent:
                    self.deleteTorrent(torrent['id'])
                if 'error' in torrent:
                    xbmcgui.Dialog().ok("error in RD",torrent['error'])
            except:
                pass
            return None
    def singleMagnetToLink_season(self, magnet,tv_movie,season,episode,dp=None):
       
        try:
            if not dp:
                dp = xbmcgui . DialogProgress ( )
                dp.create("Real Debrid","addMagnet Season", "", '')
            
            
            if self.ClientSecret == '':
                self.auth()
            '''
            hash = str(re.findall(r'btih:(.*?)&', magnet)[0].lower())
            hashCheck = self.checkHash(hash)
            fileIDString = ''
        
            if hash in hashCheck:
                
                if 'rd' in hashCheck[hash]:
                    if len(hashCheck[hash]['rd'])>0:
                        for key in hashCheck[hash]['rd'][0]:
                            fileIDString += ',' + key
            '''
          
            try:
                #hash = str(re.findall(r'btih:(.*?)&', link)[0].lower())
                hash=magnet.split('btih:')[1]
                if '&' in hash:
                    hash=hash.split('&')[0]
            except:
                hash =magnet.split('btih:')[1]
                    
            hashCheck = self.checkHash(hash)
      
            all_paths=[]
            key_list=[]

            for storage_variant in hashCheck[hash.lower()]['rd']:
                key_list = key_list+storage_variant.keys()
                
            for itt in storage_variant:
                if  not ('.mkv' in storage_variant[itt]['filename'] or '.avi' in storage_variant[itt]['filename']  or '.mp4' in storage_variant[itt]['filename']) :
                    
                
                    if itt in key_list:
                        key_list.remove(itt)
            counter_index=0
            found=False
            
           
     
           
            torrent = self.addMagnet(magnet)
            
            dp.create("Real Debrid",Addon.getLocalizedString(32193), "", '')
            res= requests.get(torrent['uri']+ "?auth_token=%s" % self.token).json()
            jump=False
            
            if res['status']=='waiting_files_selection':
                   
                fileIDString = ''
                
                f_id=''
                if len(res['files'])>0:
                    max_size=0
                    sel=[]
                    countet_index=0
                   
                    for items in res['files']:
                        if tv_movie=='tv':
                           a=1
                        else:
                            
                            if items['bytes']>max_size:
                                max_size=items['bytes']
                              
                                if 'id' in items:
                                    f_id=str(items['id'])
                                    
                            key_list=[f_id]
                        
                    start_file=','.join(key_list)
                    
                    if len(key_list)==0:
                      xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32289))).encode('utf-8'))
                    if 'id' in torrent:
                        
                        self.torrentSelect(torrent['id'], start_file)#go
                        jump=True
                            
            f_size=0
            size=0
            status=''
         
            if not jump:
                while status!='downloaded':
                   
                    status=res['status']
                    size=res['bytes']
                    unit=''
                    unit2=''
                    f_size=0
                    f_size2=0
                    if size>1024:
                        f_size=float(size)/1024
                        unit='Kb'
                    if size>(1024*1024):
                        f_size=float(size)/(1024*1024)
                        unit='Mb'
                    if size>(1024*1024*1024):
                        f_size=float(size)/(1024*1024*1024)
                        unit='Gb'
                    size2=res['original_bytes']
                    if size2>1024:
                        f_size2=float(size2)/1024
                        unit2='Kb'
                    if size2>(1024*1024):
                        f_size2=float(size2)/(1024*1024)
                        unit2='Mb'
                    if size2>(1024*1024*1024):
                        f_size2=float(size2)/(1024*1024*1024)
                        unit2='Gb'
                    seed=''
                    if 'seeders' in res:
                    
                        seed='S-'+str(res['seeders'])
                    if 'speed' in res:
                        unit3='b/s'
                        f_size3=res['speed']
                        if res['speed']>1024:
                            f_size3=float(res['speed'])/1024
                            unit3='Kb/s'
                        if res['speed']>(1024*1024):
                            f_size3=float(res['speed'])/(1024*1024)
                            unit3='Mb/s'
                        if res['speed']>(1024*1024*1024):
                            f_size3=float(res['speed'])/(1024*1024*1024)
                            unit3='Gb/s'
                        
                        speed=str(round(f_size3,2))+unit3
                    else:
                        speed=''
                    prog=0
                    if 'progress' in res:
                        prog=res['progress']
                    dp.update(prog, res['status']+' [COLOR yellow]'+seed+' '+speed+'[/COLOR]', res['original_filename'], str(round(f_size,2))+' '+unit+'/'+str(round(f_size2,2))+' '+unit2)
                    xbmc.sleep(1000)
                    res= requests.get(torrent['uri']+ "?auth_token=%s" % self.token).json()
                    
                    if res['status']=='waiting_files_selection':
                       
                        fileIDString = ''
                        
                        f_id=''
                        if len(res['files'])>0:
                            max_size=0

                            for items in res['files']:
                                if items['bytes']>max_size:
                                    max_size=items['bytes']
                                    if 'id' in items:
                                        f_id=items['id']
                                sel.append(f_id)
                            start_file=f_id
                            
                            if f_id=='':
                              xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32289))).encode('utf-8'))
                            if 'id' in torrent:
                            
                                self.torrentSelect(torrent['id'], start_file)#go
                            else:
                                xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32289))).encode('utf-8'))
                                return
                    if dp.iscanceled():
                        if 'id' in torrent:
                            self.deleteTorrent(torrent['id'])
                        dp.close()
                        return
            if not dp:
                dp.close()
            try:
                #link = self.torrentSelect(torrent['id'],  start_file)
                
                link = self.torrentInfo(torrent['id'])
           
                counter_index=0
                if tv_movie=='movie':
                    selected_index=0
                for items in link['files']:
        
             
                   if str(items['id']) in key_list:
                    #logging.warning('in1')
                    if  '.mkv' in items['path'] or '.avi' in items['path']  or '.mp4' in items['path'] :
                        
                      if 's%se%s.'%(season,episode)  in items['path'].lower() or 's%se%s '%(season,episode)  in items['path'].lower():
                        #logging.warning(items)
                        selected_index=counter_index
                        #logging.warning('in2')
                        found=True
                        break
                    if items['selected']==1:
                      #logging.warning(items)
                      counter_index+=1
                  
                if 'links' not in link:
                    xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), Addon.getLocalizedString(32289))).encode('utf-8'))
                    if dp.iscanceled():
                        self.deleteTorrent(torrent['id'])
                        dp.close()
                        return 'stop'
                    self.deleteTorrent(torrent['id'])
                    return None
                #logging.warning('selected_index::'+str(selected_index))
                if 'links' in link and len(link['links'])>0:
                    link = self.unrestrict_link(link['links'][selected_index])
                    if  not ('.mkv' in link or '.avi' in link  or '.mp4' in link) :
                        self.deleteTorrent(torrent['id'])
                        return None
                else:
                    xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), 'No streamable link found_2')).encode('utf-8'))
                    self.deleteTorrent(torrent['id'])
                    return None
                self.deleteTorrent(torrent['id'])
            except Exception as e:
                
                xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), str(e))).encode('utf-8'))
                if 'id' in torrent:
                    self.deleteTorrent(torrent['id'])
                return None
          
            return link
      
        except Exception as e:
            
            import linecache
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            
            
            line = linecache.getline(filename, lineno, f.f_globals)
            xbmc.executebuiltin((u'Notification(%s,%s)' % (Addon.getAddonInfo('name'), 'Line:'+str(lineno)+' E:'+str(e))).encode('utf-8'))
            logging.warning('ERROR IN RD torrent :'+str(lineno))
            logging.warning('inline:'+line)
            logging.warning(e)
           
            logging.warning('BAD RD torrent')
            try:
                if 'id' in torrent:
                    self.deleteTorrent(torrent['id'])
                if 'error' in torrent:
                    xbmcgui.Dialog().ok("error in RD",torrent['error'])
          
            except:
                pass
            return None
    '''
    def magnetToLink(self, torrent, args):
        try:
            logging.warning('Magnet to link')
            if torrent['package'] == 'single':
                return self.singleMagnetToLink(torrent['magnet'])

            hash = str(re.findall(r'btih:(.*?)&', torrent['magnet'])[0].lower())
            hashCheck = self.checkHash(hash)
            torrent = self.addMagnet(torrent['magnet'])
            episodeStrings, seasonStrings = source_utils.torrentCacheStrings(args)
            file_key = None
            logging.warning('Magnet to link1111')
            for storage_variant in hashCheck[hash]['rd']:
                if len(storage_variant) > 1:
                    continue
                else:
                    key = list(storage_variant.keys())[0]
                    filename = storage_variant[key]['filename']

                    if any(source_utils.cleanTitle(episodeString) in source_utils.cleanTitle(filename) for episodeString in episodeStrings):
                        if any(filename.lower().endswith(extension) for extension in
                               source_utils.COMMON_VIDEO_EXTENSIONS):
                            file_key = key
                            break
            if file_key == None:
                logging.warning('Magnet to link2222')
                self.deleteTorrent(torrent['id'])
                return None
            logging.warning('Magnet to link3333')
            self.torrentSelect(torrent['id'], file_key)
            logging.warning("torrent['id']")
            logging.warning(torrent['id'])
            link = self.torrentInfo(torrent['id'])
            logging.warning(link)
            
            link = self.unrestrict_link(link['links'][0])
            logging.warning(link)
            if link.endswith('rar'):
                link = None

            if Addon.getSetting('rd.autodelete') == 'true':
                self.deleteTorrent(torrent['id'])
            return link
        except:
            import traceback
            traceback.print_exc()
            self.deleteTorrent(torrent['id'])
            return None
    '''
    def getRelevantHosters(self):
        
        try:
            host_list = self.get_url('hosts/status')
            valid_hosts = []
            for domain, status in host_list.iteritems():
                if status['supported'] == 1 and status['status'] == 'up':
                    valid_hosts.append(domain)
            return valid_hosts
        except:
            
            return []
