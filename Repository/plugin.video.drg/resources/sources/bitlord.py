# -*- coding: utf-8 -*-
import requests,re
import time

global global_var,stop_all#global
global_var=[]
stop_all=0

 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,cloudflare_request,all_colors,base_header
from  resources.modules import cache
from resources.modules import  PTN
try:
    from resources.modules.general import Addon
except:
  import Addon
type=['movie','tv','torrent']

import urllib2,urllib,logging,base64,json

def _get_token_and_cookies( url):
    response = requests.get(url)
    token_id = re.findall(r'token\: (.*)\n', response.content)[0]
  
    token = ''.join(re.findall(token_id + r" ?\+?\= ?'(.*)'", response.content))

    cookies = ''
    for cookie in response.cookies:
        cookies += '%s=%s;' % (cookie.name, cookie.value)

    return (token, cookies)
    
def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    all_links=[]
    url='https://bitlordsearch.com'
    token, cookies=_get_token_and_cookies( url)
    headers = {
        'x-request-token': token,
        'cookie': cookies
    }
    if tv_movie=='tv':
        if Addon.getSetting('debrid_select')=='0' :
            query=[clean_name(original_title,1).replace(' ','+')+'+s%s'%(season_n),clean_name(original_title,1).replace(' ','+')+'+s%se%s'%(season_n,episode_n),clean_name(original_title,1).replace(' ','+')+'+season+' +season]
            query=[clean_name(original_title,1).replace(' ','+')+'+season+' +season]
        else:
            query=[clean_name(original_title,1).replace(' ','+')+'+s%se%s'%(season_n,episode_n)]
            
    else:
        query=[clean_name(original_title,1).replace(' ','+')+'+'+show_original_year]
    for qrr in query:
      
        
        data = {
            'query': qrr,
            'offset': 0,
            'limit': 99,
            'filters[field]': 'seeds',
            'filters[sort]': 'desc',
            'filters[time]': 4,
            'filters[category]': 3 if tv_movie=='movie' else 4,
            'filters[adult]': False,
            'filters[risky]': False
        }

        response = requests.post("https://bitlordsearch.com" + "/get_list", data, headers=headers,timeout=10).json()
        for el in response['content']:
        
            
                
                
                
               
            try:    
                size = int(el['size'])
                if size == 0:
                    continue
                else:
                    if size < 120 and el['source'] == 'thePirateBay':
                        size = size * 1024
                    elif size > 122880:
                        size = int(size / 1024)
                    elif size < 120:
                        continue
                size=size/1000
            except: pass
            
            
            
            if 1:#check and check1:
               
               
                max_size=int(Addon.getSetting("size_limit"))
                title=el['name']
                #logging.warning(title)
                if '4k' in title:
                      res='2160'
                elif '2160' in title:
                      res='2160'
                elif '1080' in title:
                      res='1080'
                elif '720' in title:
                      res='720'
                elif '480' in title:
                      res='480'
                elif '360' in title:
                      res='360'
                else:
                      res='HD'

                if size<max_size:
                              
                       all_links.append((el['name'],el['magnet'],str(size),res))
                   
                       global_var=all_links
    return global_var
        
    