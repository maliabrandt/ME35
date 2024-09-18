from machine import Pin, PWM
from time import sleep
import asyncio

class Aservo:
    def __init__(self):
        # Set up PWM on GPIO pin 5 (you can change this to any other pin)
        self.servo = PWM(Pin(5))
        self.servo.freq(50)  # Set the frequency to 50Hz for servo control
        self.run = False

    # Function to set the angle of the servo
    def set_servo_angle(self,angle):
        # Convert angle to duty cycle (between 1000 and 9000 microseconds)
        duty = int(1000 + (angle / 180) * 8000)
        self.servo.duty_u16(duty)

    async def cont_rot(self):
        while self.run:
            for i in range(5,145,1):
                self.set_servo_angle(i)
                await asyncio.sleep_ms(100)
            for i in range(145,5,-1):
                self.set_servo_angle(i)
                await asyncio.sleep_ms(100)
        #set to 0 once out of loop
        self.servo.duty_u16(0)
                
    async def stop_rot(self):
        self.servo.duty_u16(0)
        await asyncio.sleep_ms(20)

    async def main(self):
        task1 = asyncio.create_task(self.cont_rot())
        await asyncio.gather(task1)


serve = Aservo()

asyncio.run(serve.main())
