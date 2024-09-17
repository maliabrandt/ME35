#Project: Nightlight part 1
#Purpose: using pico, code a nightlight that turn on/off with MQTT commands. Once on, 
#it should have an LED brightening and dampening, and the neopixel light should be red. 
#When the button is pressed, a buzzer should sound, and the neopixel should change color. 
#Authors: Malia Brandt and Apurva Lyengar
####################################################setup########################################
#import all modules needed
from mqtt import MQTTClient
import machine, neopixel, time, asyncio
from machine import Pin, PWM

#for connecting to the WiFi
from secrets import WiFi


#connect to the WiFi!
wf = WiFi()
wf.connect_home()

#################################################begin code############################################

class nightlight:
    def __init__(self):
        #setting up MQTT communication variables
        self.mqtt_broker = 'broker.hivemq.com' 
        self.port = 1883
        self.topic_sub = 'ME35-24/#'       # this reads anything sent to ME35
        self.topic_pub = 'ME35-24/tell'

        #setup MQTT communcation 
        self.client = MQTTClient('ME35_chris', self.mqtt_broker , self.port, keepalive=60)
        

        #variable to start/stop the code -- starts off
        self.begin = False

        #setup for neopixel
        self.on = (40,0,0)  # Red color
        self.off = (0,40,0) # Green color
        self.off_all = (0,0,0) # off
        self.led = neopixel.NeoPixel(Pin(28),1)
        self.button = Pin('GPIO20', Pin.IN)
    
        #setup for buzzer
        self.buzzer = PWM(Pin('GPIO18', Pin.OUT))
        self.buzzer.freq(440)
        self.buzzer.duty_u16(0)

    #define callback for receiving messages with MQTT
    #turns begin to true when on message received
    #turns begin to false when off message received
    def callback2(self, topic, msg):
        print('received')
        if topic.decode() == 'ME35-24/Malia' and msg.decode() == 'on': #must be sent to /Malia 
            self.begin = True
            print('turn on')
        elif topic.decode() == 'ME35-24/Malia' and msg.decode() == 'off': #must be sent to /Malia
            self.begin = False
            print('turn off')

    def setup(self):
        self.client.connect()
        print('Connected to %s MQTT broker' % (self.mqtt_broker))
        self.client.set_callback(self.callback2)          # set the callback if anything is read
        self.client.subscribe(self.topic_sub.encode())   # subscribe to a bunch of topics

    #asyncio function that turns buzzer on and changes neopixel 
    #color when the button is pressed
    #function also checks for messages -- ending the loop on an "off" message
    async def check_button(self):
        while self.begin:
            if not self.button.value():
                self.client.check_msg()
                #turn on buzzer
                self.buzzer.duty_u16(1000)
                #turn led red
                self.led[0] = self.on
                self.led.write()
                await asyncio.sleep_ms(10)
            else:
                self.client.check_msg()
                #turn off buzzer
                self.buzzer.duty_u16(0)
                #turn led green
                self.led[0] = self.off
                self.led.write()
                await asyncio.sleep_ms(10)
        #turn off neopixel and buzzer when loop stops
        self.led[0]=self.off_all
        self.led.write()
        self.buzzer.duty_u16(0)
    
    #asyncio function controlling the breathing LED 
    #periodically checks messages -- ending the loop when "off" message is received
    async def breathe(self):
        f = machine.PWM(machine.Pin('GPIO0', machine.Pin.OUT))
        f.freq(50)
        while self.begin:
    		#ramping on 
            for i in range(0,65535,500):
                self.client.check_msg()
                await asyncio.sleep_ms(10)
                f.duty_u16(i)     #  u16 means unsighed 16 bit integer (0-65535)
            #dampening 
            for i in range(65535, 0, -500):
                self.client.check_msg()
                await asyncio.sleep_ms(10)
                f.duty_u16(i)

    
    #main function that runs tasks and checks for messages     
    async def main(self):
        self.setup()
        while True: #looping, checking messages
            self.client.check_msg()
            if self.begin: #once "on" message is received, run the tasks to completion 
                task1 = asyncio.create_task(self.check_button())
                task2 = asyncio.create_task(self.breathe())
                await asyncio.gather(task1, task2)

#####################################################starting main##########################################
#calling the main function

light = nightlight()
asyncio.run(light.main())


