from pysimplesoap.client import SoapClient 
from pysimplesoap.simplexml import SimpleXMLElement
from datetime import datetime,timedelta

client = SoapClient(location="http://192.168.15.68:85/WebService1.asmx",
                    action='http://tempuri.org/',
                    namespace='http://tempuri.org/',
                    soap_ns='soap', ns = False
                    )


headers = SimpleXMLElement("<Body/>")
my_test_header = headers.add_child("addCheck ")
my_test_header['xmlns']="http://tempuri.org/"
my_test_header.marshall('numCheck', 'test')
my_test_header.marshall('numTerem', 'password')
my_test_header.marshall('dtParkStart', str(datetime.now()))
my_test_header.marshall('dtParkEnd', str(datetime.now()))
my_test_header.marshall('payment', {})
my_test_header.marshall('numTerem', 'password')
my_test_header.marshall('listBond', 'password')


# print headers.rec.password
client.addCheck(rec=headers)