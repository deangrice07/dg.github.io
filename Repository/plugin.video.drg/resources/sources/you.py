# -*- coding: utf-8 -*-
#from Yu movies apk
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


import urllib2,urllib,logging,base64,json


color=all_colors[112]
def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    all_links=[]
    if tv_movie=='tv':
        return []
    headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9.0.1; samsung Build/AXXXXXXX)',

            'Connection': 'Keep-Alive'}
    c_name=clean_name(original_title,1).lower()
    url='https://yumovfreemov.com/salam/hangat.php?cai=%s&tadondo=com.yumovies.mushdomovidev'%clean_name(original_title,1)

    x=requests.get(url,headers=headers).json()
    logging.warning(x)
    
    for items in x['STREAME']:
        if c_name in items['channel_title'].lower() and show_original_year in items['channel_title']:
            url='https://yumovfreemov.com/salam/hangat.php?channel_id=%s&tadondo=com.yumovies.mushdomovidev'%items['id']
            y=requests.get(url,headers=headers).json()
            logging.warning(y)
            for itt in y['STREAME']:
                  size=0
                  try:
                        try_head = requests.get(itt['channel_url'],headers=base_header, stream=True,verify=False,timeout=3)
                    
       
                        if 'Content-Length' in try_head.headers:
                           if int(try_head.headers['Content-Length'])>(1024*1024):
                            size=(round(float(try_head.headers['Content-Length'])/(1024*1024*1024), 2))
                    
                                
                    
                  except:
                        size=0
                        
                  all_links.append((clean_name(original_title,1),'Direct_link$$$'+itt['channel_url'],str(size),'720'))

                  global_var=all_links
    return global_var