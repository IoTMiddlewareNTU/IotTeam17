from twisted.internet import reactor
from udpwkpf import WuClass, Device
import sys
from udpwkpf_io_interface import *
import socket

temp =""
flag = 0

class ReceiveData(WuClass):
    def __init__(self):
        WuClass.__init__(self)
        self.loadClass('Receive_Data')
	self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host,_ = sys.argv[2].split(':')
        self.port = 8888
        self.s.bind((self.host,self.port))
        self.s.setblocking(0)
        self.buf = [['',0,0,0,0],['',0,0,0,0]]

    def update(self,obj,pID=None,val=None):
        try:
            global temp,flag
            data,addr = self.s.recvfrom(1024)
            print addr[0] + ':' + str(addr[1]) + ' -> ' + data.strip()#addr[0]:ip address , addr[1]:port
            a,b,c,d = data.strip().split(' ')

            if flag==0:
                temp = addr[0]

            if temp==addr[0]:
                    self.buf[0][1] = int(a)
                    self.buf[0][2] = int(b)
                    self.buf[0][3] = int(c)
                    self.buf[0][4] = int(d)
            else:
                    self.buf[1][1] = int(a)
                    self.buf[1][2] = int(b)
                    self.buf[1][3] = int(c)
                    self.buf[1][4] = int(d)

            
            for j in range(0,4,1):
                sum=0
                for i in range(0,2,1):
                     sum += self.buf[i][j+1]
                obj.setProperty(j, sum)

            flag = 1
        except socket.error:
            pass
        except IOError:
            print ("Error") 

if __name__ == "__main__":
    class MyDevice(Device):
        def __init__(self,addr,localaddr):
            Device.__init__(self,addr,localaddr)
        def init(self):
            m = ReceiveData()
            self.addClass(m,0)
            self.obj_receive_data = self.addObject(m.ID)

    if len(sys.argv) <= 2:
        print 'python %s <gip> <dip>:<port>' % sys.argv[0]
        print '      <gip>: IP addrees of gateway'
        print '      <dip>: IP address of Python device'
        print '      <port>: An unique port number'
        print ' ex. python %s 192.168.4.7 127.0.0.1:3000' % sys.argv[0]
        sys.exit(-1)

    d = MyDevice(sys.argv[1],sys.argv[2])
    reactor.run()

