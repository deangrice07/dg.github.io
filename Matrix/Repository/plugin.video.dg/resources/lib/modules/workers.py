# -*- coding: utf-8 -*-
"""
	Venom Add-on
"""

from threading import Thread as thread

class Thread(thread):
	def __init__(self, target, *args, name=None):
		self._target = target
		self._args = args
		self._name = name
		thread.__init__(self, target=self._target, args=self._args, name=self._name)