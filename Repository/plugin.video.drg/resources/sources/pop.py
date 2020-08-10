# -*- coding: utf-8 -*-
import requests,re
import time

global global_var,stop_all#global
global_var=[]
stop_all=0
try:
 import xbmcgui
 local=False
except:
 local=True
 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,cloudflare_request,all_colors,base_header
try:
    from resources.modules.general import Addon
except:
  import Addon
type=['movie','tv','torrent']

import urllib2,urllib,logging,base64,json

color=all_colors[110]
def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    all_links=[]
    tmdbKey = '653bb8af90162bd98fc7ee32bcbbfb3d'
    if tv_movie=='tv':
      
       url2='http://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=external_ids'%(id,tmdbKey)
    else:
       
       url2='http://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=external_ids'%(id,tmdbKey)
    try:
        
        imdb_id=requests.get(url2,timeout=10).json()['external_ids']['imdb_id']
    except:
        imdb_id=" "
   

    
    
    if 1:
  
        x=requests.get('http://movies-v2.api-fetch.sh/%s/%s'%(tv_movie.replace('tv','show'),imdb_id),headers=base_header).json()
       

        if 'episodes' in x:
            for items in x['episodes']:
               
                if int(season)!=int(items['season']) or int(episode)!=int(items['episode']):
                    continue
             
                for items2 in items['torrents']:
            
                    if stop_all==1:
                        break
                    link=items['torrents'][items2]['url']
                    name=original_title
                    
                    seed=items['torrents'][items2]['seeds']
                    peer=items['torrents'][items2]['peers']
                    size=0
                
                    if stop_all==1:
                        break
                
                    if '4k' in items2:
                              res='2160'
                    elif '2160' in items2:
                          res='2160'
                    elif '1080' in items2:
                          res='1080'
                    elif '720' in items2:
                          res='720'
                    elif '480' in items2:
                          res='480'
                    elif '360' in items2:
                          res='360'
                    else:
                          res='HD'
                    
                     
                    try:
                         size=(float(size)/(1024*1024*1024))
                         
                    except:
                        size=0
                  
                    max_size=int(Addon.getSetting("size_limit"))
                    
                    if size<max_size:
                      
                       all_links.append((name,link,str(size),res))
                   
                       global_var=all_links
        else:
          for items in x['torrents']['en']:
            
            if stop_all==1:
                break
            link=x['torrents']['en'][items]['url']
            name=original_title
            seed=x['torrents']['en'][items]['seed']
            peer=x['torrents']['en'][items]['peer']
            size=x['torrents']['en'][items]['size']
            print size
            if stop_all==1:
                break
        
            if '4k' in items:
                      res='2160'
            elif '2160' in items:
                  res='2160'
            elif '1080' in items:
                  res='1080'
            elif '720' in items:
                  res='720'
            elif '480' in items:
                  res='480'
            elif '360' in items:
                  res='360'
            else:
                  res='HD'
            
             
            try:
                 size=(float(size)/(1024*1024*1024))
                 
            except:
                size=0
            max_size=int(Addon.getSetting("size_limit"))
            
            if size<max_size:
              
               all_links.append((name,link,str(size),res))
           
               global_var=all_links
    return global_var
        
    