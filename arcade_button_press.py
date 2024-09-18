import time
from machine import Pin
import asyncio
from servo_control import Aservo
from secrets import WiFi

class Button:
    def __init__(self):
        # initialize the button pin with the pull-up resistor
        self.button = Pin(15, Pin.IN, Pin.PULL_UP)
        self.running = False
        self.serve = Aservo()
        
        print('button created')

    async def read_button(self):
        # check the state of the button
        if self.button.value() == 0 and not self.running: #if button gets pressed and not running
            print('button pressed')
            self.running = True
            # run the servo when the button is pressed
            print('turning the servo...')
            #turn the servo on
            self.serve.run = True
            asyncio.create_task(self.serve.cont_rot())
        elif self.button.value() == 0 and self.running: #if button gets pressed and is running 
            # stop the servo when the button is pressed a second time 
            print('pressed again')
            self.running = False
            #turn servo off
            self.serve.run = False
            asyncio.create_task(self.serve.stop_rot())     

    async def monitor_button(self, debounce_delay = 0.1):
        # monitor button forever in the background
        while True:
            asyncio.create_task(self.read_button())
            await asyncio.sleep(debounce_delay)  # debounce delay
        #await asyncio.sleep_ms(100)
        
    async def main(self):
        # create a task for co-running with asyncio
        button_check = asyncio.create_task(self.monitor_button())
        await asyncio.gather(button_check)




#button = Button()  
#asyncio.run(button.main())
