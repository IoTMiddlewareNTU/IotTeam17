from twisted.internet import reactor
from udpwkpf import WuClass, Device
import sys
from udpwkpf_io_interface import *
import time

touchPadState_Pin_1 = 2
touchPadState_Pin_2 = 3
touchPadState_Pin_3 = 4

# state:0 => used ; state:1 => unused
state_1 = 0
state_2 = 0
state_3 = 0

lock_1 = 0
lock_2 = 0
lock_3 = 0

class E_Parking(WuClass):
        def __init__(self):
		WuClass.__init__(self)
		self.loadClass('E_Parking')
		self.touchPadState_gpio_1 = pin_mode(touchPadState_Pin_1, PIN_TYPE_DIGITAL, PIN_MODE_INPUT)
		self.touchPadState_gpio_2 = pin_mode(touchPadState_Pin_2, PIN_TYPE_DIGITAL, PIN_MODE_INPUT)
		self.touchPadState_gpio_3 = pin_mode(touchPadState_Pin_3, PIN_TYPE_DIGITAL, PIN_MODE_INPUT)
				
        def update(self,obj,pID=None,val=None):
			def whereID(ID):  #0:left 1:right
				if ID==1 or ID==2 or ID==4 or ID==5 or ID==8: #left
					return 0
				if ID==3 or ID==6 or ID==7 or ID==9 or ID==10: #right
					return 1

			def weightID(ID):
				if ID>=1 and ID<=4:
					return 1
				if ID>=5 and ID<=7:
					return 3
				if ID>=8 and ID<=10:
					return 9

			#load touched_pad status
			global state_1,state_2,state_3
			global lock_1,lock_2,lock_3

			#initialize
			ID_1 = obj.getProperty(0) 
			ID_2 = obj.getProperty(1) 
			ID_3 = obj.getProperty(2) 

			L_OUT_NUM = 0
			L_OUT_LOGIC = 0
			R_OUT_NUM = 0
			R_OUT_LOGIC = 0

			touchpad_1_used = 0 #0:unused 1:used
			touchpad_2_used = 0
			touchpad_3_used = 0
			if ID_1 != 0:
				touchpad_1_used = 1
			if ID_2 != 0:
				touchpad_2_used = 1
			if ID_3 != 0:
				touchpad_3_used = 1
			
			ID_1_ON_OFF = digital_read(self.touchPadState_gpio_1)
			ID_2_ON_OFF = digital_read(self.touchPadState_gpio_2)
			ID_3_ON_OFF = digital_read(self.touchPadState_gpio_3)
			
			#edge trigger 0=>1
			if state_1==0 and ID_1_ON_OFF==1 and touchpad_1_used ==1:
				lock_1 = (lock_1 + 1) % 2
			if state_2==0 and ID_2_ON_OFF==1 and touchpad_2_used ==1:
				lock_2 = (lock_2 + 1) % 2
			if state_3==0 and ID_3_ON_OFF==1 and touchpad_3_used ==1:
				lock_3 = (lock_3 + 1) % 2

			#save the history
			state_1 = ID_1_ON_OFF
			state_2 = ID_2_ON_OFF
			state_3 = ID_3_ON_OFF
			
			
			#get value by socket
			L_IN_NUM = obj.getProperty(3)
			L_IN_LOGIC = obj.getProperty(4)
			R_IN_NUM = obj.getProperty(5)
			R_IN_LOGIC = obj.getProperty(6)
			
			print 'used: '+str(touchpad_1_used)+str(touchpad_2_used)+str(touchpad_3_used)
			print 'lock: '+str(lock_1)+str(lock_2)+str(lock_3)
			#setup the value
			if lock_1 == 0 and touchpad_1_used == 1: #empty
				print 'Lock1'
				if whereID(ID_1)==0:
					L_OUT_NUM = L_OUT_NUM + 1
					L_OUT_LOGIC = L_OUT_LOGIC + L_OUT_NUM * weightID(ID_1)
				elif whereID(ID_1)==1:
					R_OUT_NUM = R_OUT_NUM + 1
					R_OUT_LOGIC = R_OUT_LOGIC + R_OUT_NUM * weightID(ID_1)

			if lock_2 == 0 and touchpad_2_used == 1: #empty
				print 'Lock2'
				if whereID(ID_2)==0:
					L_OUT_NUM = L_OUT_NUM + 1
					L_OUT_LOGIC = L_OUT_LOGIC + L_OUT_NUM * weightID(ID_2)
				elif whereID(ID_2)==1:
					R_OUT_NUM = R_OUT_NUM + 1
					R_OUT_LOGIC = R_OUT_LOGIC + R_OUT_NUM * weightID(ID_2)

			if lock_3 == 0 and touchpad_3_used == 1: #empty
				print 'Lock3'
				if whereID(ID_3)==0:
					L_OUT_NUM = L_OUT_NUM + 1
					L_OUT_LOGIC = L_OUT_LOGIC + L_OUT_NUM * weightID(ID_3)
				elif whereID(ID_3)==1:
					R_OUT_NUM = R_OUT_NUM + 1
					R_OUT_LOGIC = R_OUT_LOGIC + R_OUT_NUM * weightID(ID_3)

			#sum up
			L_OUT_NUM = L_OUT_NUM + L_IN_NUM
			L_OUT_LOGIC = L_OUT_LOGIC + L_IN_LOGIC
			R_OUT_NUM = R_OUT_NUM + R_IN_NUM
			R_OUT_LOGIC = R_OUT_LOGIC + R_IN_LOGIC

			#send value by socket
			obj.setProperty(7, L_OUT_NUM)
			obj.setProperty(8, L_OUT_LOGIC)
			obj.setProperty(9, R_OUT_NUM)
			obj.setProperty(10, R_OUT_LOGIC)

			#choose direction  
			pattern = 0
			if L_OUT_LOGIC >= R_OUT_LOGIC:
				pattern = 1#left
			if L_OUT_LOGIC < R_OUT_LOGIC:
				pattern = 2#right

			if touchpad_1_used == 0 and touchpad_2_used == 0 and touchpad_3_used == 0 #exit corner
				pattern = 2#right
			
			#encode left:00 pattern:00 right:00
			total = R_OUT_NUM + pattern * 100 +  L_OUT_NUM * 10000
			print 'Total: '+str(total)
			obj.setProperty(11, total)#pattern

			

if __name__ == "__main__":
    class MyDevice(Device):
        def __init__(self,addr,localaddr):
            Device.__init__(self,addr,localaddr)

        def init(self):
            m = E_Parking()
            self.addClass(m,0)
            self.obj_e_parking = self.addObject(m.ID)

    if len(sys.argv) <= 2:
        print 'python %s <gip> <dip>:<port>' % sys.argv[0]
        print '      <gip>: IP addrees of gateway'
        print '      <dip>: IP address of Python device'
        print '      <port>: An unique port number'
        print ' ex. python %s 192.168.4.7 127.0.0.1:3000' % sys.argv[0]
        sys.exit(-1)

    d = MyDevice(sys.argv[1],sys.argv[2])
    reactor.run()
    device_cleanup()

