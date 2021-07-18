# -*- coding: utf-8 -*-
"""
	Venom Add-on
	NOT USED
"""

# from sys import version_info

# isPY2 = version_info[0] == 2
# isPY3 = version_info[0] == 3
# string_types = str,
# integer_types = int,
# class_types = type,
# text_type = str
# binary_type = bytes

def ensure_text(s, encoding='utf-8', errors='strict'):
	try:
		if isinstance(s, bytes):
			return s.decode(encoding, errors)
		elif isinstance(s, str):
			return s
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return s

def ensure_str(s, encoding='utf-8', errors='strict'):
	try:
		if not isinstance(s, (str, bytes)):
			from resources.lib.modules import log_utils
			return log_utils.log('not expecting type : "%s"' % type(s), __name__, log_utils.LOGDEBUG)
		elif isinstance(s, bytes):
			s = s.decode(encoding, errors)
		return s
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return s

def six_decode(txt, char='utf-8'):
	try:
		if isinstance(txt, bytes):
			txt = txt.decode(char)
		return txt
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return txt