# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from datetime import datetime, timedelta
import time
import _strptime # import _strptime to workaround python 2 bug with threads


def iso_2_utc(iso_ts):
	if not iso_ts: return 0
	delim = -1
	if not iso_ts.endswith('Z'):
		delim = iso_ts.rfind('+')
		if delim == -1:
			delim = iso_ts.rfind('-')
	if delim > -1:
		ts = iso_ts[:delim]
		sign = iso_ts[delim]
		tz = iso_ts[delim + 1:]
	else:
		ts = iso_ts
		tz = None
	if ts.find('.') > -1: ts = ts[:ts.find('.')]
	try: d = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
	except TypeError: d = datetime(*(time.strptime(ts, '%Y-%m-%dT%H:%M:%S')[0:6]))
	dif = timedelta()
	if tz:
		hours, minutes = tz.split(':')
		hours = int(hours)
		minutes = int(minutes)
		if sign == '-':
			hours = -hours
			minutes = -minutes
		dif = timedelta(minutes=minutes, hours=hours)
	utc_dt = d - dif
	epoch = datetime.utcfromtimestamp(0)
	delta = utc_dt - epoch
	try: seconds = delta.total_seconds()  # works only on 2.7
	except: seconds = delta.seconds + delta.days * 24 * 3600  # close enough
	return seconds