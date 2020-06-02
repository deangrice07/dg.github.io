# -*- coding: UTF-8 -*-


# Addon Name: Mirrorv2
# Addon id: plugin.video.mirrorv2
# Addon Provider: Cy4Root

import threading


class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)

