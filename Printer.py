#!/usr/bin/python
# -*- coding=utf-8 -*-

from types import *

class printer:
	def __init__(self,interface):
		print '<Printer.__init__()'
		self.__iface=interface
		self.__config_printer()


	def __config_printer(self):
		self.__iface.write_to_dev([0x1d,0x50,0,0])
		self.__iface.write_to_dev([0x1b,0x33,50])

	def printData(self,data):
		self.__iface.write_to_dev(data)

	def lineFeed(self):
		self.__iface.write_to_dev([0x0a])
		
	def formFeed(self):
		self.__iface.write_to_dev([0x0c])
