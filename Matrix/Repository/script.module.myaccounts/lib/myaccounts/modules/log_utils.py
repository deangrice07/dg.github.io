# -*- coding: utf-8 -*-
"""
	My Accounts
"""

from datetime import datetime
import inspect
import xbmc
from myaccounts.modules import control
from myaccounts.modules import py_tools

LOGDEBUG = xbmc.LOGDEBUG #0
LOGINFO = xbmc.LOGINFO #1
LOGNOTICE = xbmc.LOGNOTICE if control.getKodiVersion() < 19 else xbmc.LOGINFO #(2 in 18, deprecated in 19 use LOGINFO(1))
LOGWARNING = xbmc.LOGWARNING #(3 in 18, 2 in 19)
LOGERROR = xbmc.LOGERROR #(4 in 18, 3 in 19)
LOGSEVERE = xbmc.LOGSEVERE if control.getKodiVersion() < 19 else xbmc.LOGFATAL #(5 in 18, deprecated in 19 use LOGFATAL(4))
LOGFATAL = xbmc.LOGFATAL #(6 in 18, 4 in 19)
LOGNONE = xbmc.LOGNONE #(7 in 18, 5 in 19)
if py_tools.isPY2:
	debug_list = ['DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR', 'SEVERE', 'FATAL']
else:
	debug_list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL']
DEBUGPREFIX = '[COLOR red][ My Accounts %s ][/COLOR]'
LOGPATH = control.transPath('special://logpath/')


def log(msg, caller=None, level=LOGNOTICE):
	debug_enabled = control.setting('debug.enabled') == 'true'
	if not debug_enabled: return
	debug_location = control.setting('debug.location')

	try:
		if caller is not None and level != LOGERROR:
			func = inspect.currentframe().f_back.f_code
			line_number = inspect.currentframe().f_back.f_lineno
			caller = "%s.%s()" % (caller, func.co_name)
			msg = 'From func name: %s Line # :%s\n                       msg : %s' % (caller, line_number, msg)
		elif caller is not None and level == LOGERROR:
			msg = 'From func name: %s.%s() Line # :%s\n                       msg : %s' % (caller[0], caller[1], caller[2], msg)

		try: msg = msg.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
		except: pass

		try:
			if isinstance(msg, py_tools.text_type):
				msg = '%s (ENCODED)' % (py_tools.ensure_str(msg, errors='replace'))
		except: pass

		if debug_location == '1':
			log_file = control.joinPath(LOGPATH, 'myaccounts.log')
			if not control.existsPath(log_file):
				f = open(log_file, 'w')
				f.close()
			with open(log_file, 'a') as f:
				line = '[%s %s] %s: %s' % (datetime.now().date(), str(datetime.now().time())[:8], DEBUGPREFIX % debug_list[level], msg)
				f.write(line.rstrip('\r\n') + '\n')
		else:
			xbmc.log('%s: %s' % (DEBUGPREFIX % debug_list[level], msg, level))
	except Exception as e:
		xbmc.log('log.log() Logging Failure: %s' % (e), LOGERROR)


def error(message=None, exception=True):
	try:
		import sys
		if exception:
			type, value, traceback = sys.exc_info()
			addon = 'script.module.myaccounts'
			filename = (traceback.tb_frame.f_code.co_filename)
			filename = filename.split(addon)[1]
			name = traceback.tb_frame.f_code.co_name
			linenumber = traceback.tb_lineno
			errortype = type.__name__
			if py_tools.isPY3: errormessage = value
			else: errormessage = value.message or value # sometimes value.message is null while value is not
			if str(errormessage) == '': return
			if message: message += ' -> '
			else: message = ''
			message += str(errortype) + ' -> ' + str(errormessage)
			caller = [filename, name, linenumber]
		else:
			caller = None
		log(msg=message, caller=caller, level=LOGERROR)
		del(type, value, traceback) # So we don't leave our local labels/objects dangling
	except Exception as e:
		xbmc.log('log.error() Logging Failure: %s' % (e), LOGERROR)