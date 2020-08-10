# -*- coding: utf-8 -*-
#frome MediaBoxHD
import requests,re
import time

global global_var,stop_all#global
global_var=[]
stop_all=0

 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,cloudflare_request,all_colors,base_header
from  resources.modules import cache
try:
    from resources.modules.general import Addon
except:
  import Addon
type=['movie','non_rd']

import urllib2,urllib,logging,base64,json

def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    
    search_url=clean_name(original_title,1).replace(' ','%20')
    if tv_movie=='tv':
       url2='http://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=external_ids'%(id,'653bb8af90162bd98fc7ee32bcbbfb3d')
    else:
     
       url2='http://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=external_ids'%(id,'653bb8af90162bd98fc7ee32bcbbfb3d')
    
    try:
       
        imdb_id=requests.get(url2).json()['external_ids']['imdb_id']
        
    except:
        return []
        
      
    
      
    
    
    all_links=[]
    
    all_l=[]
    
    if 1:
      
        
            
        x=requests.get('https://qazwsxedcrfvtgb.info/show/'+(imdb_id),headers=base_header,timeout=10,verify=False).json()
        from resources.modules.google_solve import googledrive_resolve
   
        
     
      
       
        
                
        
        for items in x['episodes']:
                         title=clean_name(original_title,1)
                         if tv_movie=='tv':
                            res_c='720'
                            title=title+'.S%sE%s'%(season_n,episode_n)
                            if not(episode==str(items['episode']) and season==str(items['season'])):
                                continue
                         else:
                            res_c='1080'
                         if 'mb_stream' in items:
                            for key in items['mb_stream']:
                                id_lk=items['mb_stream'][key]
                         else:
                            continue
                         link='https://drive.google.com/file/d/'+id_lk+'/view'
                         
                         link2,q=googledrive_resolve(link)
                         link2=link2.split('|')
                         cookies={'DRIVE_STREAM':link2[2].split('Cookie=DRIVE_STREAM%3D')[1]}
                         
                         
                         
                         try_head = requests.get(link2[0].replace('\\',''),headers=base_header,cookies=cookies, stream=True,verify=False,timeout=15)
                         size=0
                         
                         if 'Content-Length' in try_head.headers:
          
                            if int(try_head.headers['Content-Length'])>(1024*1024):
                                size=float(try_head.headers['Content-Length'])/(1024*1024*1024)
                               
                         if '4k' in res_c:
                              res='2160'
                         elif '2160' in res_c:
                              res='2160'
                         elif '1080' in res_c:
                              res='1080'
                         elif '720' in res_c:
                              res='720'
                         elif '480' in res_c:
                              res='480'
                         elif '360' in res_c:
                              res='360'
                         else:
                              res='HD'
                              
                      
                         max_size=int(Addon.getSetting("size_limit"))
                   
                         if size<max_size:
                           
                           all_links.append((title,link,str(size),res))
                       
                           global_var=all_links
                         
    
    return global_var
        
    