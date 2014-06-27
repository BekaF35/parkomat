from ctypes import *
from array import array
from types import *
import serial

c_array=c_ubyte*512;

class interface:

	"""docstring for device"""
	def __init__(self,devName,baudrate):

		self.__interface=serial.Serial(devName,baudrate)


	def read_from_dev(self,size):
		print "interface::read_from_dev()"
		data=self.__interface.read(size);
		return data

	def write_to_dev(self,data):
		self.__interface.write(data)

	def close(self):
		self.__interface.close()
