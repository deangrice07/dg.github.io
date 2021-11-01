# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from ast import literal_eval
from hashlib import md5
from re import sub as re_sub
from time import time
try: from sqlite3 import dbapi2 as db
except ImportError: from pysqlite2 import dbapi2 as db
from resources.lib.modules.control import existsPath, dataPath, makeFile, providercacheFile


def get(function, duration, *args):
	"""
	:param function: Function to be executed
	:param duration: Duration of validity of cache in hours
	:param args: Optional arguments for the provided function
	"""
	try:
		rev_args = args[:9] # discard extra args after "premiered" in getSources() from hash/key so preScrape cache key is the same.
		key = _hash_function(function, rev_args)
		cache_result = cache_get(key)
		if cache_result:
			result = literal_eval(cache_result['value'])
			if _is_cache_valid(cache_result['date'], duration):
				return result

		fresh_result = repr(function(*args)) # may need a try-except block for server timeouts
		invalid = False
		try:  # Sometimes None is returned as a string instead of None type for "fresh_result"
			if not fresh_result: invalid = True
			elif fresh_result == 'None' or fresh_result == '' or fresh_result == '[]' or fresh_result == '{}': invalid = True
			elif len(fresh_result) == 0: invalid = True
		except: pass

		if invalid: # If the cache is old, but we didn't get "fresh_result", return the old cache
			if cache_result: return result
			else: return None # do not cache_insert() None type, sometimes servers just down momentarily
		else:
			cache_insert(key, fresh_result)
			return literal_eval(fresh_result)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None

def cache_get(key):
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		ck_table = dbcur.execute('''SELECT * FROM sqlite_master WHERE type='table' AND name='cache';''').fetchone()
		if not ck_table: return None
		results = dbcur.execute('''SELECT * FROM cache WHERE key=?''', (key,)).fetchone()
		return results
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return None
	finally:
		dbcur.close() ; dbcon.close()

def cache_insert(key, value):
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		now = int(time())
		dbcur.execute('''CREATE TABLE IF NOT EXISTS cache (key TEXT, value TEXT, date INTEGER, UNIQUE(key));''')
		update_result = dbcur.execute('''UPDATE cache SET value=?,date=? WHERE key=?''', (value, now, key))
		if update_result.rowcount == 0:
			dbcur.execute('''INSERT INTO cache Values (?, ?, ?)''', (key, value, now))
		dbcur.connection.commit()
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	finally:
		dbcur.close() ; dbcon.close()

def remove(function, *args):
	try:
		key = _hash_function(function, args)
		key_exists = cache_get(key)
		if key_exists:
			dbcon = get_connection()
			dbcur = get_connection_cursor(dbcon)
			dbcur.execute('''DELETE FROM cache WHERE key=?''', (key,))
			dbcur.connection.commit()
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	try: dbcur.close() ; dbcon.close()
	except: pass

def cache_clear_providers():
	cleared = False
	try:
		dbcon = get_connection()
		dbcur = get_connection_cursor(dbcon)
		for t in ['cache', 'rel_src', 'rel_url']:
			dbcur.execute('''DROP TABLE IF EXISTS {}'''.format(t))
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
	dbcon = db.connect(providercacheFile, timeout=60) # added timeout 3/23/21 for concurrency with threads
	dbcon.row_factory = _dict_factory
	return dbcon

def get_connection_cursor(dbcon):
	dbcur = dbcon.cursor()
	dbcur.execute('''PRAGMA synchronous = OFF''')
	dbcur.execute('''PRAGMA journal_mode = OFF''')
	return dbcur

def _dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description): d[col[0]] = row[idx]
	return d

def _hash_function(function_instance, *args):
	return _get_function_name(function_instance) + _generate_md5(args)

def _get_function_name(function_instance):
	return re_sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))
# function=<function Sources.getConstants.<locals>.cache_prDict at 0x000001AE601D0AF0>
# function=<bound method Sources.getSources of <resources.lib.modules.sources.Sources object at 0x000001AE66533670>>

def _generate_md5(*args):
	md5_hash = md5()
	try: [md5_hash.update(str(arg)) for arg in args]
	except: [md5_hash.update(str(arg).encode('utf-8')) for arg in args]
	return str(md5_hash.hexdigest())

def _is_cache_valid(cached_time, cache_timeout):
	now = int(time())
	diff = now - cached_time
	return (cache_timeout * 3600) > diff