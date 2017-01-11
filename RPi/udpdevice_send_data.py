from twisted.internet import reactor
from udpwkpf import WuClass, Device
import sys
from udpwkpf_io_interface import *
import socket


class SendData(WuClass):
    def __init__(self):
        WuClass.__init__(self)
        self.loadClass('Send_Data')
	self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        myip,_ = sys.argv[2].split(':')
        self.subnet,_ = myip.rsplit('.',1)
        self.host = '127.0.0.1'
        self.port = 8888
        self.now = [0]*4 

    def update(self,obj,pID=None,val=None):
        try:
            if self.host != self.subnet+'.'+str((int)(obj.getProperty(0))):
                self.host = self.subnet+'.'+str((int)(obj.getProperty(0)))
                print 'Destination IP: ' + self.host
            for i in range(4):
		self.now[i] = (int)(obj.getProperty(i+1))
	    mess = ' '.join(str(self.now[j]) for j in range(4))
            self.s.sendto(str(mess), (self.host,self.port))
            print mess + ' -> ' + self.host + ':' + str(self.port)
        except IOError:
            print ("Error")

if __name__ == "__main__":
    class MyDevice(Device):
        def __init__(self,addr,localaddr):
            Device.__init__(self,addr,localaddr)
        def init(self):
            m = SendData()
            self.addClass(m,0)
            self.obj_send_data = self.addObject(m.ID)

    if len(sys.argv) <= 2:
        print 'python %s <gip> <dip>:<port>' % sys.argv[0]
        print '      <gip>: IP addrees of gateway'
        print '      <dip>: IP address of Python device'
        print '      <port>: An unique port number'
        print ' ex. python %s 192.168.4.7 127.0.0.1:3000' % sys.argv[0]
        sys.exit(-1)

    d = MyDevice(sys.argv[1],sys.argv[2])
    reactor.run()

