#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

class rsa:
	def __init__(self):
		pass



####################################################################################################################################
# Функция проверки числа на простоту
####################################################################################################################################
	def __isPrime(self,n):
		a_list=[]
		a=0
		s=0
		x=0
	# ????? ? ?????	?? ??????????0
		if n%2==0:
			return 0 
			
	# ????????? ??? n-1 ??? 2^s*t
		else:
			t=(n-1)
			while t%2==0:
				t=t/2
				s=s+1
	# ???? ??????????????????? random ??? ?????? ? ?????? ? ??? 			
		for i in range(s):
			while 1:
				a=random.randint(2,n-2)
				if a_list.count(a):
					continue
				else:
					a_list.append(a)
					break
			#print 'a	:	',a		
	# ???? ???? x=a^t mod N		
			x=self.__involution(a,t,n)
			#print 'x	:	',x
			
	# ????? ??????? ?=1 ???=n-1 ????? ? ????? ???? ???(????? ???? "?)
			if x==1 or x==n-1:
				continue
				
	# ???"B" ????????? x=x^2 mod N  	s-1 ??
			for j in range(s-1):
				x=(x**2)%n
				#print 'x=x^2 mod N	:	',x
				if x==1:
					return 0
				if x==n-1:
					break
			if x==n-1:
				continue
			return 0
		return 1


####################################################################################################################################
# ???? ????? ????? ? ???
####################################################################################################################################
	def __involution(self,a,n,N):
		k=[]
		r=0
		res=a

		while not n/2==0:
			k.append(n%2)
			n=n/2
			r+=1
		k.append(n)
		k.reverse()
		
		for i in range(1,r+1):
			res=((res**2)*(a**k[i]))%N
		return res


####################################################################################################################################
# ???? ???? ???????? ???
####################################################################################################################################
	def __isCoprime(self,d,m):
	  while d:
	        m, d = d, m % d
	  return m	

####################################################################################################################################
# ???? ?????? ????? ????
####################################################################################################################################

	def __findClosedKey(self,m,d):
		if d==0:
			x=1
			y=0
			return y
		x1=1
		x2=0
		y1=0
		y2=1
		while d:
			q=m/d
			r=m%d
			x=x1-q*x2
			y=y1-q*y2
			m=d
			d=r
			x1=x2
			x2=x
			y1=y2
			y2=y
		return y1

####################################################################################################################################
####################################################################################################################################


####################################################################################################################################
# Функция генерирует 'p' и 'q' простие числа заданной длины
####################################################################################################################################

	def __pqGeneration(self,ln):
		p=random.randint(2**(ln-1)+1,2**ln)
	
		while 1 :
			res=self.__isPrime(p)
			if res==1:
				break
			else:
				p=p+1

		q=random.randint(2**(ln-1)+1,2**ln)
	
		while 1 :
			res=self.__isPrime(q)
			if res==1:
				break
			else:
				q=q+1
		return(p,q)



	def DEgeneration(self,ln):
		pq=self.__pqGeneration(ln)
		p=pq[0]
		print "p=",p
		
		q=pq[1]
		print "q=",q

		n=p*q
		print "n=",n

		m=(p-1)*(q-1)
		print "m=",n

		d=random.randint(0,m-1)
		while 1:
			res=self.__isCoprime(d,m)
			if  res==1:
				print "d=",d
				break
			else:
				d=d+1

		e=self.__findClosedKey(m,d)
		if e<0:
			e=e+m
		print "e = ",e
		return(d,e,n)


	def code(self,data,e,n):
		return self.__involution(data,e,n)

	def decode(self,data,d,n):
		return self.__involution(data,d,n)


	
	







	


test=rsa()
keys=test.DEgeneration(64)
d=keys[0]
e=keys[1]
n=keys[2]
code=test.code(11111,e,n)
print code

print test.decode(code,d,n)




# code=involution(140303162137,d,n)
# print code
# decode=involution(code,e[1],n)
# print decode
#print a
#print "d,m=",d,m
#asd=
#print "d=",asd	

#	print ex	
#	print '###########################################################################'
#ex=isPrime(9833)
#print ex	
#n=''
#n=raw_input('input raw\n')
#while not n.isdigit():
#	print 'n-? ???'
#	n=raw_input('input raw\n')
#n=int(n)
#print type(n)
#b=isPrime(35)
#print b
