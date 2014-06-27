#!/usr/bin/python
# -*- coding=utf-8 -*-

import time
import math
	
class state:
	Power_up								=0
	Initialize								=1
	Idling									=2
	Accepting								=3
	Stacking								=4
	Returning								=5
	Unit_Disabled							=6
	Holding									=7
	Device_Busy								=8
	Rejecting_due_to_Insertion				=9
	Rejecting_due_to_Magnetic				=10
	Rejecting_due_to_Remained_bill_in_head	=11
	Rejecting_due_to_Multiplying			=12
	Rejecting_due_to_Conveying				=13
	Rejecting_due_to_Identification1		=14
	Rejecting_due_to_Verification			=15
	Rejecting_due_to_Optic					=16
	Rejecting_due_to_Inhibit				=17
	Rejecting_due_to_Capacity				=18
	Rejecting_due_to_Operation				=19
	Rejecting_due_to_Length					=20
	Drop_Cassette_Full						=21
	Drop_Cassette_out_of_position			=23
	Validator_Jammed						=24
	Drop_Cassette_Jammed					=25
	Cheated									=26
	Pause									=27
	Stack_Motor_Failure						=28
	Transport_Motor_Speed_Failure			=29
	Transport_Motor_Failure					=30
	Aligning_Motor_Failure					=31
	Initial_Cassette_Status_Failure			=32
	Optic_Canal_Failure						=33
	Magnetic_Canal_Failure					=34
	Capacitance_Canal_Failure				=35
	Escrow_position							=36
	Bill_stacked							=37
	Bill_returned							=38
	
	
	
class bill_validator:
	
	def __init__(self,interface,maxSum):
		self.__interface=interface
		self.__addrDev=3
		self.denom_table=[]
		self.cursum=0
		self.__maxsum=maxSum
		self.__tx_buff=bytearray()
		self.__rx_buff=bytearray()
		self.isEnable=0
		self.inEnable=0
		self.inDisable=0
		self.states=state()

		self.codeValuteTable=[]																													# ???????
		self.bondList=[]																														# ?? ????? ??????? ??????????????? ???
		self.clPayment={'clPayment':{'money': None,'codeValute':None,'typePayment':None}}														# ???? ????? ???? ?????
		self.Payment={'money': None,'codeValute':None,'typePayment':None}																		# ???? ????? ????????
		

		
		
		
##############################################################################################################
# ???? ?????? ?????? ???
##############################################################################################################
	
	def calc_crc(self,data):
		crc=0
		for i in data:
			crc^=i
			for j in range(8):
				if(crc & 0x0001):
					crc >>=1
					crc ^=0x8408
				else: crc >>=1
		return crc
		
		

##############################################################################################################
# ???? ???? ??????? ????????
##############################################################################################################
	
	def __request(self,data):
		print "BillValidator::__request()\n"
		
		self.__tx_buff=bytearray()
		self.__tx_buff.append(0x02)
		self.__tx_buff.append(self.__addrDev)
		self.__tx_buff.append(len(data)+5)
		self.__tx_buff.extend(data)
		crc=self.calc_crc(self.__tx_buff)
		print crc
		self.__tx_buff.append(crc%0x100)
		self.__tx_buff.append((crc/0x100)&0xff)
		
		for i in range(len(self.__tx_buff)):
			print "BILL VALIDATOR CMD byte[",i,']',self.__tx_buff[i]
		
		self.__interface.write_to_dev(self.__tx_buff)

		
		
		
##############################################################################################################
# ???? ??????????????
##############################################################################################################	
		
	def reset(self):
		print '<BillValidator.reset()'

		self.__request([0x30])

		res=self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.reset()::ILLEGAL COMMAND'
			print '/BillValidator.reset()>'
			return -3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.reset()::NAK received'
			print '/BillValidator.reset()>'
			return -4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.reset()::ACK received'
			print '/BillValidator.reset()>'
			return 0		



##############################################################################################################
# ???? ????? ????????????
##############################################################################################################	

	def getStatus(self):
		print '<BillValidator.getStatus()'

		self.__request([0x31])
		self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.getStatus()::ILLEGAL COMMAND'
			print '/BillValidator.getStatus()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.getStatus()::NAK received'
			print '/BillValidator.getStatus()>'
			return 4
		print '/BillValidator.getStatus()>'
		return 0
			


##############################################################################################################
# ???? ???????? ??????
##############################################################################################################	

	def setSecurity(self,y1,y2,y3):
		print '<BillValidator.setSecurity()'

		self.__request([0x31,y1,y2,y3])
		self.getAnsw()
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.setSecurity()::ILLEGAL COMMAND'
			print '/BillValidator.setSecurity()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.setSecurity()::NAK received'
			print '/BillValidator.setSecurity()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.setSecurity()::ACK received'
			print '/BillValidator.setSecurity()>'
			return 0		

			

##############################################################################################################
# ???? ?????? ?? ???
##############################################################################################################	

	def enable(self,y1,y2,y3,y4,y5,y6):
		print '<BillValidator.enable()'
		
		self.inEnable=0
		self.__isEnable=1
		self.__inEnable=1

		self.__request([0x34,y1,y2,y3,y4,y5,y6])
		res=self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.enable()::ILLEGAL COMMAND'
			print '/BillValidator.enable()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.enable()::NAK received'
			print '/BillValidator.enable()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.enable()::ACK received'
			print '/BillValidator.enable()>'
			return 0	
		


##############################################################################################################
# ???? ?????? ?? ???
##############################################################################################################	

	def disable(self):
		print '<BillValidator.disable()'
		
		self.inDisable=0
		self.__isEnable=0
		self.__inDisable=1

		self.__request([0x34,0,0,0,0,0,0])
		res=self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.disable()::ILLEGAL COMMAND'
			print '/BillValidator.disable()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.disable()::NAK received'
			print '/BillValidator.disable()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.disable()::ACK received'
			print '/BillValidator.disable()>'
			return 0	


##############################################################################################################
# ???? ????? ???
##############################################################################################################	
		
	def stack(self):
		print '<BillValidator.stack()'

		self.__request([0x35])
		self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.stack()::ILLEGAL COMMAND'
			print '/BillValidator.stack()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.stack()::NAK received'
			print '/BillValidator.stack()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.stack()::ACK received'
			print '/BillValidator.stack()>'
			return 0	
	
	
	
##############################################################################################################
# ???? ???? ???
##############################################################################################################	

	def return_(self):
		print '<BillValidator.return_()'

		self.__request([0x36])
		self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.return_()::ILLEGAL COMMAND'
			print '/BillValidator.return_()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.return_()::NAK received'
			print '/BillValidator.return_()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.return_()::ACK received'
			print '/BillValidator.return_()>'
			return 0

	
	
	
##############################################################################################################
# ???? ??????? ????????
##############################################################################################################
	
	def identification(self):
		print '<BillValidator.identification()'
		self.__request([0x37])
		self.getAnsw()


		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.identification()::ILLEGAL COMMAND'
			print '/BillValidator.identification()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.identification()::NAK received'
			print '/BillValidator.identification()>'
			return 4
		print '/BillValidator.identification()>'
		return 0
	
	
	
##############################################################################################################
# ???? ????? ??? ?????
##############################################################################################################

	def hold(self):
		print '<BillValidator.hold()'
		self.__request([0x38])
		res=self.getAnsw()


		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.hold()::ILLEGAL COMMAND'
			print '/BillValidator.hold()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.hold()::NAK received'
			print '/BillValidator.return_()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.hold()::ACK received'
			print '/BillValidator.hold()>'
			return 0

	
	
##############################################################################################################
# ???? ?????????? ??? ??
##############################################################################################################

	def setBarcodeParam(self,y1,y2):
		print '<BillValidator.setBarcodeParam()'

		self.__request([0x39,y1,y2])
		self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.setBarcodeParam()::ILLEGAL COMMAND'
			print '/BillValidator.setBarcodeParam()>'
			return 3
			3
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.setBarcodeParam()::NAK received'
			print '/BillValidator.return_()>'
			return 4

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x00):
			print 'BillValidator.setBarcodeParam()::ACK received'
			print '/BillValidator.setBarcodeParam()>'
			return 0
	
	

##############################################################################################################
# ???? 
##############################################################################################################

	def extrBarcodeData(self):
		print '<BillValidator.extrBarcodeData()'

		self.__request([0x3A])
		self.getAnsw()

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.extrBarcodeData()::ILLEGAL COMMAND'
			print '/BillValidator.extrBarcodeData()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.extrBarcodeData()::NAK received'
			print '/BillValidator.extrBarcodeData()>'
			return 4
		print '/BillValidator.extrBarcodeData()>'
		return 0
	
	
	
##############################################################################################################
# ???? ????? ???? ?????? ????????
##############################################################################################################

	def getBillTable(self):
		print '<BillValidator.getBillTable()'
	
		self.denom_table=[]
		self.__request([0x41])
		self.getAnsw()
		

		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.getBillTable()::ILLEGAL COMMAND'
			print '/BillValidator.getBillTable()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.getBillTable()::NAK received'
			print '/BillValidator.getBillTable()>'
			return 4
			
		for j in range(0,120,5):
			value=self.__rx_buff[3+j]*math.pow(10,self.__rx_buff[7+j])
			print 'self.__denomTable[',j/5,']	',value
			self.denom_table.append(value)
		print '/BillValidator.getBillTable()>'
		return 0
		
	
	
##############################################################################################################
# ???? ????? ????????? ???? ????????
##############################################################################################################

	def getCRC32(self):
		print '<BillValidator.getCRC32()'
		
		self.__request([0x51])
		self.getAnsw()
		
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0x30):
			print 'BillValidator.getCRC32()::ILLEGAL COMMAND'
			print '/BillValidator.getCRC32()>'
			return 3
			
		if(len(self.__rx_buff)==6 and self.__rx_buff[3]==0xff):
			print 'BillValidator.getCRC32()::NAK received'
			print '/BillValidator.getCRC32()>'
			return 4
		print '/BillValidator.getCRC32()>'
		return 0
		
	

##############################################################################################################
# ???? ????ACK ???
##############################################################################################################	
	def sendACK(self):
		print '<BillValidator.sendACK()'
		
		self.__request([0x00])
		print '/BillValidator.sendACK()>'

		
		
		
##############################################################################################################
# ???? ???? NAK ???
##############################################################################################################
		
	def sendNAK(self):
		print '<BillValidator.sendNAK()'
	
		self.__request([0xff])
		print '/BillValidator.sendNAK()>'

	
	
##############################################################################################################
# ???? ????????? ????
# ??????????? 
# 0-???
# 1-??? ????
# 2-??? ????? ???
# 3-??? ???
# 4-??? ?????????
##############################################################################################################
	
	def getAnsw(self):
		print '<BillValidator.getAnsw()'
		self.__rx_buff=[]
		
		startByte=self.get_byte(100)
		self.__rx_buff.append(startByte)
		
		addrByte=self.get_byte(10)
		self.__rx_buff.append(addrByte)
		
		lenByte=self.get_byte(10)
		self.__rx_buff.append(lenByte)
		
		time.sleep(lenByte*0.0005)
		
		respData=self.__interface.read_from_dev(lenByte-3)
		respData=bytearray(respData)

		print respData[3:]
		self.__rx_buff.extend(respData)
		crc=self.calc_crc(self.__rx_buff)
		if(crc!=0):
			raise ChecsumError("Error: Incorrect checksum")
		print '/BillValidator.getAnsw()>'
		return 0


##############################################################################################################
# ???? ??????????? ?? ?? ??M ????????????? ??? ???????? ?? ??-1
##############################################################################################################

	def get_byte(self,timeout):
		print "<BillValidator.get_byte()" 
		
		for i in range(timeout):
			time.sleep(0.001)
			rx_byte=self.__interface.read_from_dev(1)
			if (len(rx_byte)>0):
				print "/BillValidator.get_byte()>"
				return ord(rx_byte)
		raise GettingByteError('Errort timeout')
		
		
		

##############################################################################################################
# ???? ???? ????????
##############################################################################################################

	def Poll(self):
		print "<BillValidator.Poll()"
	
		# self.__interface.receive_req(self.__numch,2,0)															# ??????? ?????
		if(self.__request([0x33])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			return -1
		res=self.getAnsw()
		z1=self.__rx_buff[3]
		print "z1:=",z1
		
		if((z1==0x10) or (z1==0x11) or (z1==0x12)):
			self.reset()
			return self.states.Power_up
			
		if(z1==0x13):
			print "BillValidator.Poll::Initialize"
			if(self.identification()):
				return -1
			time.sleep(0.2)
			if(self.getBillTable()):
				return -1
			return self.states.Initialize
	
		if(z1==0x14):
			if(self.inDisable==1):
				self.disable()
				print "BillValidator.Poll::Idling"
			return self.states.Idling

		if(z1==0x15):
			print "BillValidator.Poll::Accepting"
			return self.states.Accepting
			
		if(z1==0x17):
			print "BillValidator.Poll::Stacking"
			return self.states.Stacking
			
		if(z1==0x18):
			print "BillValidator.Poll::Returning"
			return self.states.Returning
	
		if(z1==0x19):
			if(self.inEnable==1):
				self.enable(0xff,0xff,0xff,0xff,0xff,0xff)
				print "BillValidator.Poll::Unit_Disabled"
			return self.states.Unit_Disabled
			
		if(z1==0x1A):
			print "BillValidator.Poll::Holding"
			return self.states.Holding
			
		if(z1==0x1B):
			print "BillValidator.Poll::Device Busy"
			return self.states.Device_Busy
			
		if(z1==0x1C):
			print "BillValidator.Poll::rejection"
			return self.states.Rejecting_due_to_Insertion
			
		if(z1==0x41):
			print "BillValidator.Poll::Drop Cassette Full"
			return self.states.Drop_Cassette_Full
			
		if(z1==0x42):
			print "BillValidator.Poll::Drop Cassette out of position"
			return self.states.Drop_Cassette_out_of_position
			
		if(z1==0x43):
			print "BillValidator.Poll::Validator Jammed"
			return self.states.Validator_Jammed
			
		if(z1==0x44):
			print "BillValidator.Poll::Drop Cassette Jammed"
			return self.states.Drop_Cassette_Jammed
			
		if(z1==0x45):
			print "BillValidator.Poll::Cheated"
			return self.states.Cheated
			
		if(z1==0x46):
			print "BillValidator.Poll::Pause"
			return self.states.Pause
			
		if(z1==0x47):
			print "BillValidator.Poll::Failure"
			return self.states.Stack_Motor_Failure
			
		if(z1==0x80):
			z2=self.__rx_buff[4]
			print z2
			print "denom_table",self.denom_table
			sum=self.denom_table[z2]
			if((self.__isEnable==1) and (self.cursum+sum < self.__maxsum or self.cursum==0)):
				self.stack()
			else:
				self.return_()
			print "BillValidator.Poll::Escrow position"
			return self.states.Escrow_position
		if(z1==0x81):
			print "BillValidator.Poll::Bill stacked"
			z2=self.__rx_buff[4]
			print z2
			self.cursum+=self.denom_table[z2]
			self.clPayment['clPayment']['money']=int(self.denom_table[z2])
			self.clPayment['clPayment']['typePayment']='bond'
			self.clPayment['clPayment']['codeValute']=1#self.codeValuteTable[z2]
			
			self.Payment['money']=int(self.cursum)
			self.Payment['typePayment']='bond'
			self.Payment['codeValute']=1#self.codeValuteTable[z2]
			
			self.bondList.append(self.clPayment)
			print "/BillValidator.Poll()>"
			return self.states.Bill_stacked

		if(z1==0x82):
			print "BillValidator.Poll::Bill returned"
			return self.states.Bill_returned

		
	
		
		