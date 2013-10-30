# coding=utf-8

from math import radians, degrees
from datetime import timedelta

def deg2rad(deg):
	return radians(deg)


def deg2time(deg):
	result = list()
	rem = deg
	for d in [1, 60, 60]:
		resFrac = d * rem
		resInt = int(resFrac)
		rem = round(resFrac - resInt, 4)
		result.append(resInt)
	return result


def rad2deg(rad):
	return degrees(rad)


def rad2time(rad):
	return deg2time(rad2deg(rad))


def time2deg(timeDeg):
	res = 0
	for t, d in zip(timeDeg, [1, 60, 3600]):
		res += t / d
	return round(res, 4)


def time2rad(timeDeg):
	return deg2rad(time2deg(timeDeg))


def time2timeD(angTime):
	d, h = divmod(angTime[0], 24)
	m, s = angTime[1:]
	return timedelta(d, seconds=h * 3600 + m * 60 + s)


def deg2timeD(deg):
	return time2timeD(deg2time(deg))


def rad2timeD(rad):
	return time2timeD(rad2time(rad))


def chSign(value):
	return -value if value > 0 else abs(value)


def iterPair(iterable):
	for i in range(1, len(iterable)):
		yield iterable[i - 1], iterable[i]

if __name__ == '__main__':
	print('Self test is running')
	print('Converting degrees to radians and angular time')
	deg = 180
	rad = deg2rad(deg)
	angTime = deg2time(deg)
	print('\tDegrees\t=>\t{}\n\tRadians\t=>\t{}\n\tAng. time\t=>\t{}'.format(deg, rad, angTime))
	print('Converting radians to degrees and angular time')
	rad = 3.14
	deg = rad2deg(rad)
	angTime = rad2time(rad)
	print('\tRadians\t=>\t{}\n\tDegrees\t=>\t{}\n\tAng. time\t=>\t{}'.format(rad, deg, angTime))
	print('Converting angular time to degrees and radians')
	angTime = [90, 50, 0]
	deg = time2deg(angTime)
	rad = time2rad(angTime)
	print('\tAng. time\t=>\t{}\n\tDegrees\t=>\t{}\n\tRadians\t=>\t{}'.format(angTime, deg, rad))
	print('Converting all values to timedelta (human time)')
	angTimeD = time2timeD(angTime)
	degD = deg2timeD(deg)
	radD = rad2timeD(rad)
	print('\tAng. time\t{}\t=>\t{}\n\tDegrees\t{}\t=>\t{}\n\tRadians\t{}\t=>\t{}'.format(angTime, angTimeD,
		deg, degD,
		rad, radD))
