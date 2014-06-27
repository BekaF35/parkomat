#!/usr/bin/python
# -*- coding: utf-8 -*-
from interface import *
from BillValidator import *
from kd import *
from Printer import *
from PIL import Image
import qrcode 
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement
from datetime import datetime,timedelta
from RSA import rsa

#===================================================================================================

KOI8_R_to_PC865=[
0xC4,0xb3,0xDA,0xBF,0xc0,0xd9,0xc3,0xb4,0xc2,0xc1,0xc5,0xdf,0xdc,0xdb,0xdd,0xde,
0xb0,0xb1,0xb2,0xf4,0xff,0xf9,0xfb,0xf7,0xf3,0xf2,0xff,0xf5,0xf8,0xfd,0xfa,0xf6,
0xcd,0xba,0xd5,0xf1,0xd6,0xc9,0xb8,0xb7,0xbb,0xd4,0xd3,0xc8,0xbe,0xbd,0xbc,0xc6,
0xc7,0xcc,0xb5,0xf0,0xb6,0xb9,0xd1,0xd2,0xcb,0xcf,0xd0,0xca,0xd8,0xd7,0xce,0xff,
0xee,0xa0,0xa1,0xe6,0xa4,0xa5,0xe4,0xa3,0xe5,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,
0xaf,0xef,0xe0,0xe1,0xe2,0xe3,0xa6,0xa2,0xec,0xeb,0xa7,0xe8,0xed,0xe9,0xe7,0xea,
0x9e,0x80,0x81,0x96,0x84,0x85,0x94,0x83,0x95,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,
0x8f,0x9f,0x90,0x91,0x92,0x93,0x86,0x82,0x9c,0x9b,0x87,0x98,0x9d,0x99,0x97,0x9a
]

##############################################################################################################
# Класс исключения 
##############################################################################################################

class parkomatError(Exception):
	
	def __init__(self,value):
		self.value=value
		
	def __str__(self):
		return repr(self.value)
		
		

##############################################################################################################
# Класс паркомат
##############################################################################################################
class parkomat:
	
	def __init__(self,configFile):

		self.__config_File=configFile																	# Переменная содержащая путь и имя файла конфигурации


		self.__iface=0																					# Переменная для хранения экземпляра класса шины I2C
		self.__billvalidator=0																			# Переменная для хранения экземпляра класса купюроприемника
		self.__printer=0 																				# Переменная для хранения экземпляра класса принтера
		self.__kd=0
		self.__rsa=0

		
		self.__tx_buff=[]																				# tx Буффер
		self.__qr=0																					# Переменная для хранения экземпляра класса QRcode
		self.__billvalidatorLib=""																	# Переменная содержащая путь к библиотеке libi2c.so
		self.__printerLib=""																		# Переменная содержащая путь к библиотеке libi2c.so

		self.__printerDev=""																			# Переменная содержащая имя драйвера принтера
		self.__billvalidatorDev=""																		# Переменная содержащая имя драйвера купюроприемника
		self.__printerBaudrate=0																		# Переменная содержащая имя драйвера купюроприемника
		self.__billvalidatorBaudrate=0																	# Переменная содержащая имя драйвера купюроприемника

		self.__ticket_File=""																			# Переменная содержащая путь и имя файла чека	
		self.__ticket=[]																				# Массив содержащий данные чека 
		self.__img_data=[]																				# Массив содержащий данные qr кода
		
		self.__cash=0																					# Переменная содержащяя внесенную сумму последнего сеанса
		self.__hourly_rate=0																			# Переменная храняшая стоимость одного часа стоянки
		self.__period=0																					# Переменная хранящая количество оплаченных часов
		self.__max_sum=0

		self.__d=0
		self.__e=0
		self.__n=0

		self.__ticketID=''																				# Id чека
		self.__numTerm=''																				# Номер терминала
		self.__soapClient=0																				# переменнная для храниния класса клиента soap 
		self.__soapServerLocation=''																	# переменная для хранения пути к soap серверу
		self.__action=''
		self.__namespace=''																				# переменая для хранения пространства имен soap сервера
		self.__rec={}.fromkeys(['numCheck','numTerem','dtParkStart','dtParkEnd','payment','listBond'])
		self.Payment={'money': None,'codeValute':None,'typePayment':None}

		self.__config_system()																			# функция настройки системы	

##############################################################################################################
# Функция конфигурирования системы
##############################################################################################################

	def __config_system(self):
		print "parkomat.__config_system()"		
		
		fd=open(self.__config_File,"r")																	# Открытие файла конфигурации системы
		for line in fd:																					# Читаем построчно файл конфигурации
			if(line[0]=='#'):
				continue

			if(line.find("printer driver")!=-1):														# Если содержит строку 'device' извлекаем имя драйвера устройства I2C
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__printerDev=line[start:end].strip()												#
				print 'имя устройства принтера',self.__printerDev										#
				continue

			if(line.find("billvalidator driver")!=-1):													# Если содержит строку 'device' извлекаем имя драйвера устройства I2C
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__billvalidatorDev=line[start:end].strip()											#
				print 'имя устройства купюроприемника',self.__billvalidatorDev							#

			if(line.find("printer baudrate")!=-1):														# Если содержит строку 'hourly_rate' извлекаем данные стоимости одного часа стоянки
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#														
				self.__printerBaudrate=int(line[start:end].strip(''))									#					
				print 'скорость порта в бодах',self.__printerBaudrate									#

			if(line.find("billvalidator baudrate")!=-1):												# Если содержит строку 'hourly_rate' извлекаем данные стоимости одного часа стоянки
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#														
				self.__billvalidatorBaudrate=int(line[start:end].strip(''))								#					
				print 'скорость порта в бодах',self.__billvalidatorBaudrate								#


			if(line.find("hourly rate")!=-1):															# Если содержит строку 'hourly_rate' извлекаем данные стоимости одного часа стоянки
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#														
				self.__hourly_rate=int(line[start:end].strip(''))										#					
				print 'стоимость стоянки в час',self.__hourly_rate										#
			
			if(line.find("ticket file")!=-1):															# Если содержит строку 'ticket_file' извлекаем данные пути и имени файла чека
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__ticket_File=line[start:end].strip()												#
				print 'полный путь до файла чека',self.__ticket_File									#
				
			if(line.find("max sum")!=-1):																# Если содержит строку 'max sum' извлекаем максимальное значения принимаемой суммы за сеанс
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__max_sum=int(line[start:end].strip())												#
				print "максимальная принимаемая сумма",self.__max_sum									#

			if(line.find("numTerm")!=-1):																# Если содержит строку 'numTerm' извлекаем строку номера терминала
				start=line.find("=")+1																	#
				end=line.find(";",start)																#
				self.__numTerm=line[start:end].strip()													#
				print "Номер терминала: ",self.__numTerm												#
				
			if(line.find("location")!=-1):																# Если содержит строку 'location' извлекаем  путь к фискальному серверу
				start=line.find("=")+1																	#
				end=line.find(";",start)																#
				self.__soapServerLocation=line[start:end].strip()										#
				print "путь к soap серверу: ",self.__soapServerLocation									#
				#time.sleep(1)
				
			if(line.find("action")!=-1):																# Если содержит строку 'action' извлекаем  
				start=line.find("=")+1																	#
				end=line.find(";",start)																#
				self.__action=line[start:end].strip()													#
				print "действие : ",self.__action														#
				#time.sleep(1)
				
			if(line.find("namespace")!=-1):																# Если содержит строку 'namespace' извлекаем  значение пространства имен
				start=line.find("=")+1																	#
				end=line.find(";",start)																#
				self.__namespace=line[start:end].strip()												#
				print "пространство имен фискального сервера: ",self.__namespace						#

			if(line.find("key d")!=-1):																# Если содержит строку 'max sum' извлекаем максимальное значения принимаемой суммы за сеанс
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__d=int(line[start:end].strip())												#
				print "self.__d:",self.__d									#

			if(line.find("key e")!=-1):																# Если содержит строку 'max sum' извлекаем максимальное значения принимаемой суммы за сеанс
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__e=int(line[start:end].strip())												#
				print "self.__e:",self.__e									#

			if(line.find("key n")!=-1):																# Если содержит строку 'max sum' извлекаем максимальное значения принимаемой суммы за сеанс
				start=line.find("-")+1																	#
				end=line.find(" ",start)																#
				self.__n=int(line[start:end].strip())												#
				print "self.__n:",self.__n									#




		self.__printerIface=interface(self.__printerDev,self.__printerBaudrate)								# Создаем класс интерфейса принтера
		self.__billvalidatorIface=interface(self.__billvalidatorDev,self.__billvalidatorBaudrate)			# Создаем класс интерфейса купюроприемника

		self.__printer=printer(self.__printerIface)

		self.__billvalidator=bill_validator(self.__billvalidatorIface,self.__max_sum)
		if(self.__billvalidator.reset()<0):																			
			raise parkomatError('Can\'t reset a bill validator.')

		self.__kd=kd("/dev/kdXIO")

		self.__rsa=rsa()

		self.__soapClient=SoapClient(																				# создаем класс клиента фискального сервера
			location=self.__soapServerLocation,																			#
			action=self.__action,																						#
			namespace=self.__namespace,																					#
			soap_ns='soap', ns = False
			)	




##############################################################################################################
# Функция формирования данныч чека
##############################################################################################################

	def __createTicket(self):
		print "parkomat.createTicket(self)"																

		self.__ticket=[]																				# обнуление массива хранящего данные чека
		self.__ticketID=datetime.now().strftime('%y%m%d%H%M%S')											# формируем номер чека из данных даты и времени транзакции
		self.__qr=qrcode.QRCode(																		# создаем класс экземпляр класса QRcode для создания qr кода											
			version=None,																				# поле отвечает за максимальный размер qr кода
			error_correction=qrcode.constants.ERROR_CORRECT_L,											# поле отвечает за обработку ошибок
			box_size=1,																					# определяет количество пикселей в одном квадрате
			border=0,																					# ширина рамки в квадратах
		)	

		self.__qr.add_data(self.__rsa.code(int(self.__ticketID),self.__e,self.__n))						# и кодируем строку в qrcode
		


		fd=open(self.__ticket_File,"r")																	# Открываем файл чека
		for line in fd:																					# читаем построчно данные чека
			line=line.rstrip('\n')																		# удаляем символы переноса строки из всех строчек
			
			if(line.find("Налич")!=-1):																	# если строка содержит строку "Налич" 
				line=line.format(str(self.__cash))														# добавляем в конец строки данные внесенных наличных
				# self.__qr.add_data(line)																# и кодируем строку в qrcode
				
			if(line.find("Опл. в ч")!=-1):																# если строка содержит строку "Опл. в ч" 
				line=line.format(str(self.__hourly_rate))												# добавляем в конец строки данные стоимости услуги в час
				# self.__qr.add_data(line)																# и кодируем строку в qrcode
				
			self.__period=(self.__cash/self.__hourly_rate)												# расчет времени по внесенной сумме
			if(line.find("Кол. часов")!=-1):															# если строка содержит строку "Кол. часов" 
				line=line.format(str(self.__period))													# добавляем в конец строки данные времени по внесенной сумме
				# self.__qr.add_data(line)																# и кодируем строку в qrcode
			
			if(line.find("Номер чека")!=-1):															# если строка содержит строку "Номер чека" 
				line=line.format(self.__ticketID)														# 
				#self.__qr.add_data(line)																# 
			
			
			line=line.decode('utf-8')																	# преобразование строки из кодировки utf-8
			line=line.encode('koi8-r')																	# в кодировку koi8-r и добавление в масив данных чека 
			
			strData=[]																					# буфер для хранения данных перекодированной строки(PC437)/обнуление 																				
			for ch in line:																				# читаем строку посимвольно
				if(ord(ch)<0x80):																		# если байт < 0x80 добавляем в буффер strData
					strData.append(ord(ch))																# иначе преобразуем к таблице кодировки PC437 [U.S.A.,Standart Europe]
				else:																					#
					strData.append(KOI8_R_to_PC865[ord(ch)-0x80])										#
			self.__ticket.append(strData)																# 

		fd.close()																						# закрываем фаил чека
		
		self.__qr.make(fit=True)																		# сохраняем qrcode в виде изображения в формате .png
		img=self.__qr.make_image()																		# и вызываем функцию по преобразованию картинки qr кода в масив символов
		img.save('qrcode.png')																			#
		self.__conversionQrcode()																		#																	#
	
	
	
	
##############################################################################################################
# Функция преобразования изображения qrcode.png в массив данных
##############################################################################################################
	
	def __conversionQrcode(self):
		self.__img_data=[]																				# обнуление массива хранящего данные qr кода
		
		img=Image.open('qrcode.png')																	# открываем изображение с qr кодом
		pix_val=list(img.getdata())																		# считываем данные пикселей изображения
		size=img.size																					# получение размера изображения в пикселях
		width=size[0]																					#
		heigh=size[1]																					#
	
		if(heigh%2):																					# проверяем высоту изображения если нечетная 
			for k in range(width):																		# добавляем в массив pix_val один ряд из
				pix_val.append(255)																		# белых пикселей (это делается так как анализ идет по 2 м строкам пикселей)
			heigh=heigh+1																				#
	
		for i in range(0,heigh,2):																		# Анализируем массив с данными пикселей изображения
			img_row=[]																					# создаем массив который хранит данные 2х строк пикселей
			
			for j in range(width):																		#
				index=i*(width)+j																		# вычисляем индекс данных пикселя массива pix_val[]
				if(pix_val[index]==pix_val[index+width]==255):											# и анализируем пиксель и пиксель след строки с тем же смещением
					img_row.append(0x20)																# если = между собой и = 255 добавляем в массив img_row[] символ 0x20(таблица кодировки PC437 [U.S.A.,Standart Europe])
				if(pix_val[index]==pix_val[index+width]==0):											# если = между собой и = 0 добавляем в массив img_row[] символ 0xDB(таблица кодировки PC437 [U.S.A.,Standart Europe])
					img_row.append(0xDB)																# если 1й пиксель > 2го соответственно добавляем в массив img_row[] символ 0xDС(таблица кодировки PC437 [U.S.A.,Standart Europe])
				if(pix_val[index]>pix_val[index+width]):												# если 1й пиксель < 2го соответственно добавляем в массив img_row[] символ 0xDF(таблица кодировки PC437 [U.S.A.,Standart Europe])
					img_row.append(0xDC)																#
				if(pix_val[index]<pix_val[index+width]):												#
					img_row.append(0xDF)																#
					
			self.__img_data.append(img_row)																# Добавляем массив img_row[] в массив self.__img_data[]
			
			
##############################################################################################################
# Функция печати чека
##############################################################################################################		
			
	def print_ticket(self):	
		print "parkomat.print_ticket()"

		self.__createTicket()																			# вызов функции формирования данных чека
		for i in self.__ticket:																			# читаем данные из массива с данными чека построчно
			self.__printer.printData(i)																	# передаем данные tx буффера в канал принтера
			self.__printer.lineFeed()																	# перенос строки принтера см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80
				
		for k in range(len(self.__img_data)):															# читаем и передаем данные qr кода в канал принтера
			self.__printer.printData(self.__img_data[k])												# если ошибка возвращаем 0
			self.__printer.lineFeed()																	# перенос строки принтера см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80
		self.__printer.formFeed()																		# обрезка и предоставление чека см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80




##############################################################################################################
# Функция приема наличных
##############################################################################################################					
				
	def receiving_bills(self):
		self.__kd.readLine()																			# Очищаем буффер kd устройства
		self.__cash=0																					#
		status=0																						# переменная состояния купюроприемника
		while(1):																						# и запускаем пулинг купюроприемника

			time.sleep(0.2)																				# задержка в 200 мс
			status=	self.__billvalidator.Poll()															#

			if(status==-1):																				#
				self.__billvalidator.sendNAK()															#
				raise parkomatError('Error in Poll() command')											#
			self.__billvalidator.sendACK()																#
			
			if(status==self.__billvalidator.states.Unit_Disabled):										# проверяем статус если disabled даем команду enabled
				self.__billvalidator.enable(0xff,0xff,0xff,0xff,0xff,0xff)								#
			
			if(self.__cash!=self.__billvalidator.cursum):												#
				self.__cash=self.__billvalidator.cursum													#
				self.display('Внесенно-{}р.'.format(self.__cash))										#
				
			if(status==self.__billvalidator.states.Idling):												# проверяем статус если Idling 
				fl=self.__kd.rd(1)																		# проверяем не была ли нажата кнопка оплатить
				if(fl>0):																				#
					if(fl=='D'):																		# если была нажата отключаем прием купюр
						self.__billvalidator.disable()													# присваиваем переменной self.__cash принятую сумму       ??????????????????????????????????????????????????!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
						if(self.__billvalidator.Poll()==-1):											# и возвращаем принятую сумму
							self.__billvalidator.sendNAK()												#
						self.__billvalidator.sendACK()													#
						self.__billvalidator.cursum=0													#
						return self.__cash	
						
				
				
##############################################################################################################
# Функция логирования данных на сервер
##############################################################################################################		

	def loggingDataToServer(self):
		headers = SimpleXMLElement("<Body/>")
		my_test_header = headers.add_child("addCheck ")
		my_test_header['xmlns']="http://tempuri.org/"
		my_test_header.marshall('numCheck', self.__ticketID)
		my_test_header.marshall('numTerem', self.__numTerm)
		my_test_header.marshall('dtParkStart', str(datetime.now()))
		my_test_header.marshall('dtParkEnd', str(datetime.now()+timedelta(hours=int(self.__period))))
		my_test_header.marshall('payment',self.__billvalidator.Payment)
		my_test_header.marshall('listBond', self.__billvalidator.bondList)

		res=self.__soapClient.addCheck(rec=headers)
				
##############################################################################################################
# Функция возвращает стоимость услуги в час
##############################################################################################################		

	def get_hourly_rate(self):
		return self.__hourly_rate


##############################################################################################################
# Функция возвращает сумму внесенных наличных последнего сеанса
##############################################################################################################		
	def get_cash(self):
		return self.__cash


##############################################################################################################
# Функция отображения сообщения на дисплей паркомата
##############################################################################################################		

	def display(self,message):
		message=message.decode('utf-8')
		message=message.encode('koi8-r')
		self.__kd.wr(chr(0x10))
		self.__kd.wr(message)

##############################################################################################################
# конец обьявления класса Parkomat
##############################################################################################################		
		
example=parkomat("./config/config.cfg")

while(1):
	example.display('Внесите наличые и нажмите \'D\'.\n\nCтоим.усл.-{}р/ч'.format(example.get_hourly_rate()))
	if(not example.receiving_bills()):
		continue
	example.print_ticket()
	example.loggingDataToServer()
