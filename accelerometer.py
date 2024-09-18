from machine import I2C, Pin, PWM
import time, neopixel
import struct
import asyncio

class Acceleration():
    def __init__(self, scl, sda, addr = 0x62):
        self.running = False
        self.addr = addr
        self.i2c = I2C(1,scl=scl, sda=sda, freq=100000) 
        self.connected = False
        if self.is_connected():
            print('connected')
            self.write_byte(0x11,0) #start data stream

        self.red = (40,0,0)  # Red color
        self.green = (0,40,0) # Green color
        self.off = (0,0,0) # off
        self.led = neopixel.NeoPixel(Pin(28),1)

    def is_connected(self):
        options = self.i2c.scan() 
        print(options)
        self.connected = self.addr in options
        return self.connected 
            
    def read_accel(self):
        buffer = self.i2c.readfrom_mem(self.addr, 0x02, 6) # read 6 bytes starting at memory address 2
        return struct.unpack('<hhh',buffer)

    def write_byte(self, cmd, value):
        self.i2c.writeto_mem(self.addr, cmd, value.to_bytes(1,'little'))

    #make them lights dance
    async def dance(self):
        #setup
        l1= PWM(Pin('GPIO10', Pin.OUT))
        l2= PWM(Pin('GPIO11', Pin.OUT))
        l3= PWM(Pin('GPIO12', Pin.OUT))
        l4= PWM(Pin('GPIO13', Pin.OUT))
        
        l1.freq(1000)
        l2.freq(1000)
        l3.freq(1000)
        l4.freq(1000)

        #dance 
        l1.duty_u16(49151)
        await asyncio.sleep_ms(500)
        l1.duty_u16(0)
        l2.duty_u16(49151)
        await asyncio.sleep_ms(500)
        l2.duty_u16(0)
        l3.duty_u16(49151)
        await asyncio.sleep_ms(500)
        l3.duty_u16(0)
        l4.duty_u16(49151)
        await asyncio.sleep_ms(500)
        l4.duty_u16(0)
        await asyncio.sleep_ms(500)       

        #begin neopixel 
        self.led[0] = self.green
        self.led.write()
        await asyncio.sleep_ms(1000)
        self.led[0] = self.red
        self.led.write()
        await asyncio.sleep_ms(1000)
        self.led[0] = self.off
        self.led.write()


    def detect_tap(self):
        f = PWM(Pin('GPIO18', Pin.OUT))
        f.freq(440)
        
        threshold = 18000
        x,y,z = self.read_accel()
        #print(x,y,z)
        magnitude = (x**2 + y**2 + z**2) ** 0.5
        
        #print("magnitude", magnitude)
        if magnitude > threshold: ##sum greater than, this means tapped:
            self.running = True
            f.duty_u16(1000)
            #print('tapped!!!')
            asyncio.create_task(self.dance())
            self.running = False
            return True
        else: ##then has not been tapped
            f.duty_u16(0)
            #print('not tapped!!!')
            return False

    async def run(self):
        while True:
            #print(self.running)
            if not self.running:
                self.detect_tap()
                await asyncio.sleep_ms(50)

#scl = Pin('GPIO27', Pin.OUT)
#sda = Pin('GPIO26', Pin.OUT)

#t = Acceleration(scl, sda)
#asyncio.run(t.run())
