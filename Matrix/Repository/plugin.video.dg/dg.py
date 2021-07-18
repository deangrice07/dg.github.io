# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from sys import argv
from urllib.parse import parse_qsl
from resources.lib.modules import router

if __name__ == '__main__':
	try:
		url = dict(parse_qsl(argv[2].replace('?', '')))
	except:
		url = {}
	router.router(url)