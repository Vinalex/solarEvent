# coding=utf-8

from datetime import  timedelta, date, datetime
from math import floor, sin, cos, tan, asin, acos, atan
from tools import *
import cities

class Sun:
	def __init__(self, city=cities.Moscow):
		#Словарь интервала дат + 2 даты (крайние для расчета солнечного дня), со значениями восхода\захода
		self.dateRangeSun = dict()
		#Объект - город, содержащий параметры координат и часового смещения
		self.city = city
		#Углы зенита для разных положения солнца
		self.zenith = {'Offical': time2deg([90, 50, 0]),
					   'Civil': time2deg([96, 0, 0]),
					   'Nautical': time2deg([102, 0, 0]),
					   'Astronomical': time2deg([108, 0, 0])}

	#Главная функция
	def getResult(self, dates=date.today().strftime('%d.%m.%Y')):
		#Получаем диапазон дат, dstetime
		dates = self._datesRange(dates)
		#Для всез дат из диапазона
		for focusDate in dates:
			#Получаем параметры солнца
			self._getSun(focusDate)

	#Создания списка дат из диапазона
	def _datesRange(self, dates):
		dates = {datetime.strptime(focusDate, '%d.%m.%Y').date() for focusDate in dates.split('-')}
		if len(dates) == 2:
			dateBegin, dateEnd = sorted(dates)
			daysRange = dateEnd-dateBegin
			for i in range(daysRange.days+1):
				dates.add(dateBegin+timedelta(i))
		return dates

	#Получение параметров солнца
	def _getSun(self, focusDate):
		#Список смещений для соседей
		directDisp = range(-1, 2)
		#Срез с данными мз 3х дат для расчета светового и темного дня
		section = list()
		#Для всех смещений
		for disp in directDisp:
			#Получаем дату со смещением относительно фокусной даты
			dispDate = focusDate + timedelta(disp)
			#Если такой даты в глобальном списке нет, то
			if not dispDate in self.dateRangeSun:
				#Определяем параметры солнца в глобальном словаре дат
				self.dateRangeSun[dispDate] = self._sunInfo(dispDate)
			#Попутно, составляем список-срез из 3х дат для расчета светлого и темного времени суток
			section.append([self.dateRangeSun[dispDate], chSign(disp)])
		#ПРоверяем, если для фокусной даты, уже расчитаны эти параметры, то опускаем расчеты
		if not (self.dateRangeSun[focusDate].get('Light') and self.dateRangeSun[focusDate].get('Dark')):
			self.dateRangeSun[focusDate].update(self._lightDark(section))

	#Общая функция вызова расчетов восхода и закаат солнца
	def _sunInfo(self, focusDate):
		return {'Sunrise': self._sunrise(focusDate),
				'Sunset': self._sunset(focusDate)}

	#индивидуальные параметры для расчета восхода
	def _sunrise(self, focusDate):
		ft = lambda dayOfYear, lngHour: dayOfYear + ((6 - lngHour) / 24)
		fH = lambda cosH: 360 - rad2deg(acos(cosH))
		fUT = lambda T, lngHour: T - lngHour
		#Вызываем калькулятор с индивидуальными параметрами
		return self._calculate(focusDate, ft, fH, fUT)

	#Индивидуальные параметры для расчета заката
	def _sunset(self, focusDate):
		ft = lambda dayOfYear, lngHour: dayOfYear + ((18 - lngHour) / 24)
		fH = lambda cosH: rad2deg(acos(cosH))
		fUT = lambda T, lngHour: 24 - abs(T - lngHour)
		#Вызываем калькулятор с индивидуальными параметрами
		return self._calculate(focusDate, ft, fH, fUT)

	#Функция, для расчета светлого и емного времени суток
	def _lightDark(self, section):
		#Список - "отрезок", со всеми событиями за сегодняшний день (т.к. их возможно больше 2х)
		line = list()
		#Условимся, что изначально, у нас 24 часа - темно. (Одни сутки)
		lTime, dTime = timedelta(0), timedelta(1)
		#Возможные типы солнца
		sunTypes = ['Sunrise', 'Sunset']
		#Разбераем срез. В нем, dateSunInfo - инф. о Солнце, и величина обратного смещения даты.
		for dateSunInfo, backDisp in section:
			#Перебераем типы, для навигации по словарю
			for sunType in sunTypes:
				#Получаем дату события, [тип][тип зенита], и пребавляем к ней обратное смещения
				focus = dateSunInfo[sunType]['Offical'] + timedelta(backDisp)
				#Прибавляем, для того, чтобы понять, возможно это событие произошло в нашу дату?
				#Например, есть дата со смещение -1 от нужной, прибавив к ней обратное смещение получим 0
				#И если это так, то, вчерашнее событие, например - закат, произошел сегодня
				if focus.days == 0:
					#Собераем список сегодняшних событий
					line.append((sunType, dateSunInfo[sunType]['Offical']))
		#Определяем начало и конец списка-отрезка
		#Если первая величина - закат, значит начало - восход, ибо до заката, всегда восход и наоборот
		first = [('Sunrise', timedelta(0)) if line[0][0] == 'Sunset' else ('Sunset', timedelta(0))]
		#То же самое для конца отрезка
		last = [('Sunrise', timedelta(1)) if line[-1][0] == 'Sunset' else ('Sunset', timedelta(1))]
		#Собераем отрезок
		line = first + line + last
		#iterPair - разберает отрезок на пары значений, со смещением=1
		for pair in iterPair(line):
			#Получаем тип события
			pairType = [x[0] for x in pair]
			#И его значение
			pairVal = [x[1] for x in pair]
			#Если событие - Восход-Закат
			if pairType == ['Sunrise', 'Sunset']:
				#Значит - в это время было светл
				#ПРибавляем к свету, разницу во времени между Закатом и Восходом
				lTime += pairVal[1] - pairVal[0]
		#А темно было, ровно столько, сколько небыло светло (=
		dTime -= lTime
		return {'Light': lTime,
				'Dark': dTime}

	#Функция-калькулятор, для расчета времени события
	def _calculate(self, focusDate, ft, fH, fUT):
		calculation = dict()
		dayOfYear = int(focusDate.strftime('%j'))
		latitude = self.city.latitude
		longitude = self.city.longitude
		lngHour = longitude / 15
		t = ft(dayOfYear, lngHour)
		sunPos = (0.9856 * t) - 3.289
		lngSun = sunPos + (1.916 * sin(deg2rad(sunPos))) + (0.020 * sin(deg2rad(2 * sunPos))) + 282.634 - 360
		RA = rad2deg(atan(0.91764 * tan(deg2rad(lngSun))))
		Lquadrant = floor(lngSun / 90) * 90
		RAquadrant = floor(RA / 90) * 90
		RA = (RA + (Lquadrant - RAquadrant)) / 15
		sinDec = 0.39782 * sin(deg2rad(lngSun))
		cosDec = cos(asin(sinDec))
		for name, deg in self.zenith.items():
			cosH = (cos(deg2rad(deg)) - (sinDec * sin(deg2rad(latitude)))) / (cosDec * cos(deg2rad(latitude)))
			if cosH > 1:
				localT = None
			elif cosH < -1:
				localT = None
			else:
				H = fH(cosH) / 15
				T = H + RA - (0.06571 * t) - 6.622
				UT = fUT(T, lngHour)
				localT = deg2timeD(UT + self.city.timeOffset)
			calculation[name] = localT
		return calculation


if __name__ == '__main__':
	MoscowSun = Sun(cities.Moscow)
	MoscowSun.getResult('01.01.2014-01.01.2015')
	for d in MoscowSun.dateRangeSun:
		print(d)
		for s in MoscowSun.dateRangeSun[d]:
			if s in ['Dark', 'Light']:
				print(s, MoscowSun.dateRangeSun[d][s])
			else:
				for t in MoscowSun.dateRangeSun[d][s]:
					print(s, t, MoscowSun.dateRangeSun[d][s][t])



