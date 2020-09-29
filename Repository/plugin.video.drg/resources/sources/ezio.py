# -*- coding: utf-8 -*-
import re
import time

global global_var,stop_all#global
global_var=[]
stop_all=0
from  resources.modules.client import get_html
 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,all_colors,base_header
from  resources.modules import cache
try:
    from resources.modules.general import Addon
except:
  import Addon
type=['tv','torrent']

import urllib2,urllib,logging,base64,json

def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    all_links=[]
    if tv_movie=='movie':
        return []
    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
    if tv_movie=='tv':
      
       url2='http://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=external_ids'%(id,tmdbKey)
    else:
       
       url2='http://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=external_ids'%(id,tmdbKey)
    try:
        
        imdb_id=get_html(url2,timeout=10).json()['external_ids']['imdb_id']
    except:
        imdb_id=" "
        
    allow_debrid=True
    search_url=('%s-s%se%s'%(clean_name(original_title,1).replace(' ','-'),season_n,episode_n)).lower()
    for pages in range(0,3):
        x=get_html('https://eztv.io/api/get-torrents?imdb_id=%s&limit=100&page=%s'%(imdb_id.replace('tt',''),str(pages)),headers=base_header,timeout=10).json()
        
        max_size=int(Addon.getSetting("size_limit"))
        dev_num=1024*1024*1024
        for items in x['torrents']:
                    title=items['filename']
                   
                    if 's%se%s.'%(season_n,episode_n) not in title.lower():
                        continue
                    lk=items['magnet_url']
                    size=(float(items['size_bytes'])/dev_num)
                    
               
                    
                    if int(size)<max_size:
                       if '2160' in title:
                              res='2160'
                       if '1080' in title:
                              res='1080'
                       elif '720' in title:
                              res='720'
                       elif '480' in title:
                              res='480'
                       elif '360' in title:
                              res='360'
                       else:
                              res='HD'

                     
                      
                       all_links.append((title,lk,str(size),res))
                   
                       global_var=all_links
    return global_var
        
    