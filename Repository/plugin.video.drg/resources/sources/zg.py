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
type=['movie','tv','torrent']

import urllib2,urllib,logging,base64,json

def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    all_links=[]
    if tv_movie=='tv':
        cat='205'
    elif tv_movie=='movie':
        cat='201'
    else:
        cat='0'
    if tv_movie=='movie':
     search_url=[('%s+%s'%(clean_name(original_title,1).replace(' ','+'),show_original_year)).lower()]
    elif tv_movie=='tv':
     if Addon.getSetting('debrid_select')=='0' :
        search_url=[('%s+s%se%s'%(clean_name(original_title,1).replace(' ','+'),season_n,episode_n)).lower(),('%s+s%s'%(clean_name(original_title,1).replace(' ','+'),season_n)).lower(),('%s+season+%s'%(clean_name(original_title,1).replace(' ','+'),season)).lower()]
     else:
        search_url=[('%s+s%se%s'%(clean_name(original_title,1).replace(' ','+'),season_n,episode_n)).lower()]
    for itt in search_url:
        x=requests.get('https://zooqle.com/search?q={0}+%2Blang%3Aen'.format(itt,cat),headers=base_header,timeout=10).content
        
        regex_pre='<tr (.+?)</tr>'
        m_pre=re.compile(regex_pre,re.DOTALL).findall(x)
        for items in m_pre:
        
            regex='<a title="Magnet link".+?href="(.+?)">.+?class="progress-bar prog-blue prog-l.+?>(.+?).+?title="Seeders: (.+?) \| Leechers: (.+?)"'
            match=re.compile(regex,re.DOTALL).findall(items)
           
            for links,size,seed,peer in match:
                size=size.replace('&nbsp;'," ")
                if stop_all==1:
                    break
                try:
                     o_size=size
                     size=float(o_size.replace('GiB','').replace('MiB','').replace('GB','').replace('MB','').replace(",",'').strip())
                     if 'MB' in o_size or 'MiB' in o_size:
                       size=size/1000
                except:
                    size=0
                regex='dn=(.+?)&'
                
                nam=re.compile(regex).findall(links)[0]
                max_size=int(Addon.getSetting("size_limit"))
                if '.TS.' in nam:
                    continue
                if int(size)<max_size:
                   if '4k' in nam:
                          res='2160'
                   elif '2160' in nam:
                          res='2160'
                   elif '1080' in nam:
                          res='1080'
                   elif '720' in nam:
                          res='720'
                   elif '480' in nam:
                          res='480'
                   elif '360' in nam:
                          res='360'
                   else:
                          res='HD'
                   try:
                        nam=urllib.unquote_plus(nam).replace('[zooqle.com]','').strip()
                   except:
                       pass
                   all_links.append((nam,links,str(size),res))
               
                   global_var=all_links
    return global_var
        
    