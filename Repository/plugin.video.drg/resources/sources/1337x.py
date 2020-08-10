# -*- coding: utf-8 -*-
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
type=['movie']

import urllib2,urllib,logging,base64,json

def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    
    search_url=clean_name(original_title,1).replace(' ','%20')
    
        
      
    
      
    
    
    all_links=[]
    
    all_l=[]
    
    if 1:
      
        
            
        x=requests.get('https://1337xmovies.org/search?s='+(search_url),headers=base_header,timeout=10,verify=False).content
        regex='<div class="box-item"(.+?)</div'
        m_pre=re.compile(regex,re.DOTALL).findall(x)
      
        for item in m_pre:
            regex='a href="(.+?)".+?title="(.+?)"'
            m=re.compile(regex,re.DOTALL).findall(item)
            for lk,nm in m:
                if nm.lower()!=clean_name(original_title,1).lower():
                    continue
                
                y=requests.get(lk,headers=base_header,timeout=10,verify=False).content
               
                if tv_movie=='tv':
                    regex_p='<div id="tv-seasons">(.+?)<h2 class="page-header">'
                    m_l=re.compile(regex_p,re.DOTALL).findall(y)[0]
                    regex='a href="(.+?)".+?title="(.+?)"'
                    nn=re.compile(regex,re.DOTALL).findall(m_l)
                    y=''
                    for itt,tt in nn:
                        
                        if 'season %s episode %s '%(season,episode) in tt:
                           
                            y=requests.get(itt,headers=base_header,timeout=10,verify=False).content
                            
                regex='<tr>(.+?)</tr>'
                m2_pre=re.compile(regex,re.DOTALL).findall(y)
                for items in m2_pre:
                    regex='<td>(.+?)<.+?<td class="text-center">(.+?)<.+?a href="magnet(.+?)"'
                    m2=re.compile(regex,re.DOTALL).findall(y)
                    title=clean_name(original_title,1)
                    if tv_movie=='tv':
                        title=title+'.S%sE%s'%(season_n,episode_n)
                    for size,res_c,link in m2:
                    
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
                        try:
                             o_size=size.decode('utf8','ignore')
                             
                             size=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                             if 'MB' in o_size:
                               size=size/1000
                        except Exception as e:
                            
                            size=0
                
        
        
                              
                      
                        max_size=int(Addon.getSetting("size_limit"))
                   
                        if size<max_size:
                           
                           all_links.append((title,'magnet'+link,str(size),res))
                       
                           global_var=all_links
                         
    
    return global_var
        
    