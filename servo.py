
import RPi.GPIO as GPIO
import time

from config import *

class Servo:
    def __init__(self):
        self.pin = Config.SERVO_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)
        
        self.cover_opened = False

    def set_angle(self, angle):
        duty_cycle = 2 + (angle / 18)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

    def open_cover(self):
        self.set_angle(90)
        self.cover_opened = True
    
    def close_cover(self):
        self.set_angle(0)
        self.cover_opened = False
