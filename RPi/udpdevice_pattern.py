from udpwkpf import WuClass, Device
import sys
from udpwkpf_io_interface import *
from twisted.internet import reactor
#import pyupm_lpd8806
from raspledstrip.ledstrip import *

nLED = 2
#mystrip = pyupm_lpd8806.LPD8806(nLED,7)
led = LEDStrip(nLED)

max7219_decodeMode = 0x09
max7219_intensity = 0x0a
max7219_scanLimit = 0x0b
max7219_shutdown = 0x0c
max7219_displayTest = 0x0f

mDigit = [ 0b11111100, 0b01100000, 0b11011010, 0b11110010, 0b01100110, 0b10110110, 0b00111110, 0b11100000, 0b11111110, 0b11100110, 0b10111010 ]
mUp = [ 0b10001100, 0b11100000 ]
mDown = [ 0b00011100, 0b01110000 ]
mRight = [ 0b11110000, 0b10010000 ]
mLeft = [ 0b10011100, 0b10010000 ]

dataPin = 5
loadPin = 6
clockPin = 7

class mPattern(WuClass):
	def __init__(self):
		WuClass.__init__(self)
		self.loadClass('Seg_Pattern')
		self.data_gpio = pin_mode(dataPin, PIN_TYPE_DIGITAL, PIN_MODE_OUTPUT)
		self.load_gpio = pin_mode(loadPin, PIN_TYPE_DIGITAL, PIN_MODE_OUTPUT)
		self.clock_gpio = pin_mode(clockPin, PIN_TYPE_DIGITAL, PIN_MODE_OUTPUT)
	
	def update(self,obj,pID=None,val=None):
		try:
			def mShiftOut(val):
				for i in range(0,8,1):
					flag = 0
					if val & (1<<(7-i)):
						flag = 1
					digital_write(self.data_gpio, flag)
					digital_write(self.clock_gpio, 1)
					digital_write(self.clock_gpio, 0)
	
			def mSetCMD(command, val):
				digital_write(self.load_gpio, 0)
				mShiftOut(command)
				mShiftOut(val)
				digital_write(self.load_gpio, 0)
				digital_write(self.load_gpio, 1)
		
			def mDisplay(n1, n2, n3):
				for i in range(1,9,1):
					o = 0b0000000
					t = (mDigit[n1]>>(8-i)) & 1
					w = 0b1111111 & t<<6
					o = o | w
					t1 = 0
					t2 = 0
					if n2 == 1:
						t1 = mLeft[1]
						t2 = mLeft[0]
					elif n2 == 2:
						t1 = mUp[1]
						t2 = mUp[0]
					t1 = (t1>>(8-i)) & 1
					w = 0b1111111 & t1<<5
					o = o | w
					t2 = (t2>>(8-i)) & 1
					w = 0b1111111 & t2<<4
					o = o | w
					t = (mDigit[n3]>>(8-i)) & 1
					w = 0b1111111 & t<<3
					o = o | w
					mSetCMD(i,o)
						
			digital_write(self.clock_gpio, 1)
			mSetCMD(max7219_intensity, 0x0f)
			mSetCMD(max7219_scanLimit, 0x07)
			mSetCMD(max7219_decodeMode, 0x00)
			mSetCMD(max7219_shutdown, 0x01)
			mSetCMD(max7219_displayTest, 0x00)
			
			num = obj.getProperty(0)
			
			n1 = num % 100
			n2 = int(num / 100) % 100
			n3 = int(num / 10000)
			
			mDisplay(n1,n2,n3)
			
			if n2 == 1:
				led.fillRGB(255,0,0,0,0)
				led.update()
				led.fillRGB(0,255,0,1,1)
				led.update()
				#mystrip.show()
				#mystrip.setPixelColor(0, 125, 0, 0)
				#mystrip.setPixelColor(1, 0, 125, 0)
				#mystrip.show()
			elif n2 == 2:
				led.fillRGB(0,255,0,0,0)
				led.update()
				led.fillRGB(255,0,0,1,1)
				led.update()
				#mystrip.show()
				#mystrip.setPixelColor(0, 0, 125, 0)
				#mystrip.setPixelColor(1, 125, 0, 0)
				#mystrip.show()
			print num,n1,n2,n3
		except IOError:
			print ("Error")
	
if __name__ == "__main__":
    class MyDevice(Device):
        def __init__(self,addr,localaddr):
            Device.__init__(self,addr,localaddr)

        def init(self):
            cls = mPattern()
            self.addClass(cls,0)
            self.obj_mpattern = self.addObject(cls.ID)

    if len(sys.argv) <= 2:
        print 'python %s <gip> <dip>:<port>' % sys.argv[0]
        print '      <gip>: IP addrees of gateway'
        print '      <dip>: IP address of Python device'
        print '      <port>: An unique port number'
        print ' ex. python %s 192.168.4.7 127.0.0.1:3000' % sys.argv[0]
        sys.exit(-1)

    d = MyDevice(sys.argv[1],sys.argv[2])
    reactor.run()
