import os  #line:1
from  resources.modules.client import get_html
def download_file (OOOOO000O000OO000 ,O00OO00O0OOOOO0O0 ):#line:6
    OOOOO00OO000O000O =os .path .join (O00OO00O0OOOOO0O0 ,"fixed_list.txt")#line:7
    O0OO00O0OO00OOOOO =get_html (OOOOO000O000OO000 ,stream =True )#line:9
    with open (OOOOO00OO000O000O ,'wb')as O0O0O000O000O000O :#line:10
        for OOO0OO00O00O0OO00 in O0OO00O0OO00OOOOO .iter_content (chunk_size =1024 ):#line:11
            if OOO0OO00O00O0OO00 :#line:12
                O0O0O000O000O000O .write (OOO0OO00O00O0OO00 )#line:13
    return OOOOO00OO000O000O #line:15
def unzip (O00O0O0OOO00O0O00 ,OOOO0O0OOO0O0OO00 ):#line:17
    try:
        from zfile import ZipFile #line:19
    except:
        from zipfile import ZipFile
    
    OO0OOO0000O0O0O00 =O00O0O0OOO00O0O00 #line:22
    O0O0OO0OO0O0O0O0O ='Masterpenpass'#line:23
    O000000O0O0OO000O =ZipFile (OO0OOO0000O0O0O00 )#line:24
    O000000O0O0OO000O .extractall (OOOO0O0OOO0O0OO00 )#line:27
def script (OOO00OO0OO0O00OO0 ):#line:28
    OOO00OO0OO0O00OO0 =OOO00OO0OO0O00OO0 .replace ('99999****','')#line:29
    import StringIO ,gzip #line:31
    O00O000O0O0O000O0 =StringIO .StringIO ()#line:32
    O00O000O0O0O000O0 .write (OOO00OO0OO0O00OO0 .decode ('base64'))#line:33
    O00O000O0O0O000O0 .seek (0 )#line:38
    OOOO0OO000O00OOO0 =gzip .GzipFile (fileobj =O00O000O0O0O000O0 ,mode ='rb').read ()#line:39
    OOOO00OO00O0O0OOO =OOOO0OO000O00OOO0 .split ("$$$$$")#line:40
    O00O000O0O0O000O0 =StringIO .StringIO ()#line:45
    O00O000O0O0O000O0 .write (OOOO00OO00O0O0OOO [0 ].decode ('base64'))#line:46
    O00O000O0O0O000O0 .seek (0 )#line:51
    OOOO0OO000O00OOO0 =gzip .GzipFile (fileobj =O00O000O0O0O000O0 ,mode ='rb').read ()#line:52
    return OOOO0OO000O00OOO0 #line:53
def gdecom (O00OO0OOO0OO00000 ):#line:55
    if '99999****'in O00OO0OOO0OO00000 :#line:57
        return script (O00OO0OOO0OO00000 )#line:58
    import StringIO ,gzip #line:59
    O0OOO000O000000O0 =StringIO .StringIO ()#line:60
    O0OOO000O000000O0 .write (O00OO0OOO0OO00000 .decode ('base64'))#line:61
    O0OOO000O000000O0 .seek (0 )#line:66
    return gzip .GzipFile (fileobj =O0OOO000O000000O0 ,mode ='rb').read ()