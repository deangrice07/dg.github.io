# -*- coding: utf-8 -*-
"""
	dg Add-on
"""

from datetime import datetime
import inspect
import unicodedata
from resources.lib.modules.control import transPath, setting as getSetting, lang, joinPath, existsPath

LOGDEBUG = 0
# ###--from here down methods print when dg logging set to "Normal".
LOGINFO = 1
LOGWARNING = 2
LOGERROR = 3
LOGFATAL = 4
LOGNONE = 5 # not used

debug_list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL']
DEBUGPREFIX = '[COLOR white][ DG: %s ][/COLOR]'
LOGPATH = transPath('special://logpath/')


def log(msg, caller=None, level=LOGINFO):
	debug_enabled = getSetting('debug.enabled') == 'true'
	if not debug_enabled: return
	debug_level = getSetting('debug.level')
	if level == LOGDEBUG and debug_level != '1': return
	debug_location = getSetting('debug.location')
	if isinstance(msg, int): msg = lang(msg) # for strings.po translations
	try:
		if not msg.isprintable(): # ex. "\n" is not a printable character so returns False on those cases
			msg = '%s (NORMALIZED by log_utils.log())' % normalize(msg)
		if isinstance(msg, bytes):
			msg = '%s (ENCODED by log_utils.log())' % msg.decode('utf-8', errors='replace')

		if caller is not None and level != LOGERROR:
			func = inspect.currentframe().f_back.f_code
			line_number = inspect.currentframe().f_back.f_lineno
			caller = "%s.%s()" % (caller, func.co_name)
			msg = 'From func name: %s Line # :%s\n                       msg : %s' % (caller, line_number, msg)
		elif caller is not None and level == LOGERROR:
			msg = 'From func name: %s.%s() Line # :%s\n                       msg : %s' % (caller[0], caller[1], caller[2], msg)

		if debug_location == '1':
			log_file = joinPath(LOGPATH, 'dg.log')
			if not existsPath(log_file):
				f = open(log_file, 'w')
				f.close()
			with open(log_file, 'a', encoding='utf-8') as f:
				line = '[%s %s] %s: %s' % (datetime.now().date(), str(datetime.now().time())[:8], DEBUGPREFIX % debug_list[level], msg)
				f.write(line.rstrip('\r\n') + '\n')
				# f.writelines([line1, line2]) ## maybe an option for the 2 lines without using "\n"
		else:
			import xbmc
			xbmc.log('%s: %s' % (DEBUGPREFIX % debug_list[level], msg), level)
	except Exception as e:
		import traceback
		traceback.print_exc()
		import xbmc
		xbmc.log('[ plugin.video.dg ] log_utils.log() Logging Failure: %s' % (e), LOGERROR)

def error(message=None, exception=True):
	try:
		import sys
		if exception:
			type, value, traceback = sys.exc_info()
			addon = 'plugin.video.dg'
			filename = (traceback.tb_frame.f_code.co_filename)
			filename = filename.split(addon)[1]
			name = traceback.tb_frame.f_code.co_name
			linenumber = traceback.tb_lineno
			errortype = type.__name__
			errormessage = value or value.message
			if str(errormessage) == '': return
			if message: message += ' -> '
			else: message = ''
			message += str(errortype) + ' -> ' + str(errormessage)
			caller = [filename, name, linenumber]
		else:
			caller = None
		del(type, value, traceback) # So we don't leave our local labels/objects dangling
		log(msg=message, caller=caller, level=LOGERROR)
	except Exception as e:
		import xbmc
		xbmc.log('[ plugin.video.dg ] log_utils.error() Logging Failure: %s' % (e), LOGERROR)

def normalize(msg):
	try:
		# msg = ''.join(c for c in unicodedata.normalize('NFKD', py_tools.ensure_text(py_tools.ensure_str(msg))) if unicodedata.category(c) != 'Mn')
		msg = ''.join(c for c in unicodedata.normalize('NFKD', msg) if unicodedata.category(c) != 'Mn')
		return str(msg)
	except:
		error()
		return msg
