# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

import re
import unicodedata


def get(title):
	try:
		if not title: return
		title = re.sub(r'&#(\d+);', '', title).lower()
		title = re.sub(r'(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
		title = title.replace('&quot;', '\"').replace('&amp;', '&')
		# title = re.sub(r'\n|([\[({].+?[})\]])|\s(vs[.]?|v[.])\s|([:;–\-"\',!_\.\?~])|\s', '', title) # removes bracketed content
		title = re.sub(r'\n|([\[({].+?[})\]])|([:;–\-"\',!_.?~$@])|\s', '', title) # stop trying to remove alpha characters "vs" or "v", they're part of a title
		return title
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return title

def normalize(title):
	try:
		title = ''.join(c for c in unicodedata.normalize('NFKD', title) if unicodedata.category(c) != 'Mn')
		return str(title)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
		return title