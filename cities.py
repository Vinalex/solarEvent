# coding=utf-8

from tools import *

class City:
	def __init__(self, coordinates, timeOffset):
		self.latitude, self.longitude = [time2deg(x) for x in coordinates]
		self.timeOffset = timeOffset

Moscow = City(coordinates=((55, 45, 20.83), (37, 37, 3.48)), timeOffset=+4)



