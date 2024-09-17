from mqtt import MQTTClient
from secrets import WiFi
import machine, neopixel, time, asyncio
from machine import Pin, PWM
from accelerometer import Acceleration
from arcade_button_press import Button

class Nightlight2:
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
        
        #setup accelerometer
        self.scl = Pin('GPIO27', Pin.OUT)
        self.sda = Pin('GPIO26', Pin.OUT)

        self.t= Acceleration(self.scl, self.sda)
        
        #setup button
        self.butt = Button()
        
    
    #define callback for receiving messages with MQTT
    #turns begin to true when on message received
    #turns begin to false when off message received
    def callback2(self, topic, msg):
        print('received')
        if (topic.decode() == 'ME35-24/Ari-and-Malia') and (msg.decode() == 'On'): #must be sent to /Ari-and-Malia
            self.begin = True
            print('turn on')    
        elif (topic.decode() == 'ME35-24/Ari-and-Malia') and (msg.decode() == 'Off'): #must be sent to /Ari-and-Malia
            #stop checking for messages
            self.begin = False
            #stop the accelerometer
            self.t.running = False
            print('turn off')
            
    def setup(self):
        #connect to the WiFi!
        wf = WiFi()
        wf.connect_tufts()
        self.client.connect()
        print('Connected to %s MQTT broker' % (self.mqtt_broker))
        self.client.set_callback(self.callback2)          # set the callback if anything is read
        self.client.subscribe(self.topic_sub.encode())   # subscribe to a bunch of topics
           
    #main function that runs tasks and checks for messages     
    async def main(self):
        self.setup()
        while True: #looping, checking messages
            self.client.check_msg()
            if self.begin: #if On message is received
                #check button
                asyncio.create_task(self.butt.read_button())
                await asyncio.sleep(0.1)  # debounce delay for button 
                if not self.t.running: #check if the accelerometer has been turned on 
                    self.t.detect_tap()
                    await asyncio.sleep_ms(10)
                
                
        
                
nl = Nightlight2()
asyncio.run(nl.main())



