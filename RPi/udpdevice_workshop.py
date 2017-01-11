import time,sys
from udpwkpf import WuClass, Device
from udpwkpf_io_interface import *
from twisted.internet import reactor
import random
from math import log
import time

import udpdevice_e_parking
import udpdevice_pattern
import udpdevice_receive_data
import udpdevice_send_data

class MyDevice(Device):
    def __init__(self,addr,localaddr):
        Device.__init__(self,addr,localaddr)

    def init(self):
        m = udpdevice_e_parking.E_Parking()
        self.addClass(m,0)
        self.obj_e_parking = self.addObject(m.ID)
        m2 = udpdevice_pattern.mPattern()
        self.addClass(m2,0)
        self.obj_mpattern = self.addObject(m2.ID)
        m3 = udpdevice_receive_data.ReceiveData()
        self.addClass(m3,0)
        self.obj_receive_data = self.addObject(m3.ID)
        m4 = udpdevice_send_data.SendData()
        self.addClass(m4,0)
        self.obj_send_data = self.addObject(m4.ID)

if len(sys.argv) <= 2:
        print 'python udpwkpf.py <ip> <ip:port>'
        print '      <ip>: IP of the interface'
        print '      <port>: The unique port number in the interface'
        print ' ex. python udpwkpf.py 127.0.0.1 3000'
        sys.exit(-1)

d = MyDevice(sys.argv[1],sys.argv[2])

reactor.run()

