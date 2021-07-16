# -*- coding: UTF-8 -*-

import six

import os
from . import en, en_Torrent, gr

try:
    from dgscrapers.modules import cfscrape
    cfScraper = cfscrape.create_scraper()
except: pass


scraper_source = os.path.dirname(__file__)
__all__ = [x[1] for x in os.walk(os.path.dirname(__file__))][0]


##--en--##
hoster_source = en.sourcePath
hoster_providers = en.__all__


##--en_Torrent--##
torrent_source = en_Torrent.sourcePath
torrent_providers = en_Torrent.__all__


##--Foreign Providers--##
greek_providers = gr.__all__


##--All Foreign Providers--##
foreign_providers = {'gr': greek_providers}
all_foreign_providers = []
for key, value in six.iteritems(foreign_providers):
    all_foreign_providers += value


##--All Providers--##
total_providers = {'en': hoster_providers, 'en_Torrent': torrent_providers, 'gr': greek_providers}
all_providers = []
for key, value in six.iteritems(total_providers):
    all_providers += value
