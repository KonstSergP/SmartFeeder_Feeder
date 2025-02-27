import RPi.GPIO as GPIO
import time

from settings.config import *


class Servo:
    def __init__(self):
        self.pin = settings.servo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)
        
        self.cover_opened = False

 
    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()


    def set_angle(self, angle):
        duty_cycle = 2 + (angle / 18)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(0)


    def open_cover(self):
        self.set_angle(settings.open_angle)
        self.cover_opened = True
        log.info("Cover opened")


    def close_cover(self):
        self.set_angle(settings.close_angle)
        self.cover_opened = False
        log.info("Cover closed")
