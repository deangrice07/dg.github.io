# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import os
import traceback

from resources.lib.modules import client, control, log_utils


class jsonMenu(object):
    def __init__(self):
        # Default root locations, if none is set by the indexer
        self.local_root = os.path.join(control.addonPath, 'menu')
        self.menu = None

        self.agent = 'QXRyZWlkZXMgSlNPTiBNZW51x'[1:].decode('base64')

    def load(self, menu_file):
        if 'http' in menu_file:
            try:
                header = {'User-Agent': self.agent}
                response = client.request(menu_file, headers=header)
                self.menu = json.loads(response)
            except Exception:
                failure = traceback.format_exc()
                log_utils.log('jsonMenu - Open Remote Exception: \n' + str(failure))
        else:
            try:
                menu_file = os.path.join(self.local_root, menu_file)
                fileref = control.openFile(menu_file)
                content = fileref.read()
                fileref.close()
                self.menu = json.loads(content)
            except Exception:
                failure = traceback.format_exc()
                log_utils.log('jsonMenu - Open Local Exception: \n' + str(failure))
