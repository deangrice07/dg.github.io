# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from time import time
try: from sqlite3 import dbapi2 as db
except ImportError: from pysqlite2 import dbapi2 as db
from resources.lib.modules.control import existsPath, dataPath, makeFile, metacacheFile


def fetch(items, lang='en', user=''):
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='meta';''').fetchone()
		if not ck_table:
			dbcur.execute('''CREATE TABLE IF NOT EXISTS meta (imdb TEXT, tmdb TEXT, tvdb TEXT, lang TEXT, user TEXT, item TEXT, time TEXT,
			UNIQUE(imdb, tmdb, tvdb, lang, user));''')
			dbcur.connection.commit()
			dbcur.close() ; dbcon.close()
			return items
		t2 = int(time())
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	for i in range(0, len(items)):
		try:
			try: # First lookup by TVDb and IMDb, since there are some incorrect shows on Trakt that have the same IMDb ID, but different TVDb IDs (eg: Gotham, Supergirl).
				match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND tvdb=? AND lang=? AND user=? AND NOT imdb='' AND NOT tvdb='')''',
					(items[i].get('imdb', ''), items[i].get('tvdb', ''), lang, user)).fetchone()
				t1 = int(match[6])
			except:
				try: # Lookup both IMDb and TMDb for more accurate match.
					match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND tmdb=? AND lang=? AND user=? AND not imdb='' AND NOT tmdb='')''',
						(items[i].get('imdb', ''), items[i].get('tmdb', ''), lang, user)).fetchone()
					t1 = int(match[6])
				except:
					try: # Last resort single ID lookup.
						match = dbcur.execute('''SELECT * FROM meta WHERE (imdb=? AND lang=? AND user=? AND NOT imdb='') OR (tmdb=? AND lang=? AND user=? AND NOT tmdb='') OR (tvdb=? AND lang=? AND user=? AND NOT tvdb='')''',
							(items[i].get('imdb', ''), lang, user, items[i].get('tmdb', ''), lang, user, items[i].get('tvdb', ''), lang, user)).fetchone()
						t1 = int(match[6])
					except: pass
			if match:
				update = (abs(t2 - t1) / 3600) >= 720
				if update: continue
				item = eval(match[5])
				item = dict((k, v) for k, v in iter(item.items()) if v is not None and v != '')
				items[i].update(item)
				items[i].update({'metacache': True})
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
	try: dbcur.close() ; dbcon.close()
	except: pass
	return items

def insert(meta):
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		dbcur.execute('''CREATE TABLE IF NOT EXISTS meta (imdb TEXT, tmdb TEXT, tvdb TEXT, lang TEXT, user TEXT, item TEXT, time TEXT,
		UNIQUE(imdb, tmdb, tvdb, lang, user));''')
		t = int(time())
		for m in meta:
			if "user" not in m: m["user"] = ''
			if "lang" not in m: m["lang"] = 'en'
			i = repr(m['item'])
			try: dbcur.execute('''INSERT OR REPLACE INTO meta Values (?, ?, ?, ?, ?, ?, ?)''', (m.get('imdb', ''), m.get('tmdb', ''), m.get('tvdb', ''), m['lang'], m['user'], i, t))
			except: pass
		dbcur.connection.commit()
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()

def cache_clear_meta():
	cleared = False
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		dbcur.execute('''DROP TABLE IF EXISTS meta''')
		dbcur.execute('''VACUUM''')
		dbcur.connection.commit()
		cleared = True
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		cleared = False
	finally:
		dbcur.close() ; dbcon.close()
	return cleared

def get_connection():
	if not existsPath(dataPath): makeFile(dataPath)
	dbcon = db.connect(metacacheFile, timeout=60) # added timeout 3/23/21 for concurrency with threads
	# dbcon.row_factory = _dict_factory
	return dbcon

def get_connection_cursor(dbcon):
	dbcur = dbcon.cursor()
	dbcur.execute('''PRAGMA synchronous = OFF''')
	dbcur.execute('''PRAGMA journal_mode = OFF''')
	return dbcur