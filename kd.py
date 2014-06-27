class kd:

	def __init__(self,devname):
		self.fd=open(devname,'r+w')
		self.fd.write(bytearray([0x12,0x02]))

	def wr(self,data):
		print "kd::<wr()"
		self.fd.write(data)
		print "kd::wr>"
		return 1

	def rd(self,size):
		data=self.fd.read(size)
		return data

	def readLine(self):
		line=self.fd.readline()
		return line

