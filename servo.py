import RPi.GPIO as GPIO
from time import sleep

from settings.config import *


class Servo:
    def __init__(self):
        self.pin = settings.servo_pin
        self.speed = settings.servo_speed
        self.angle = None
        self.cover_opened = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)
        
        self.close_cover(True)

 
    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()


    def set_angle(self, angle, first=False):
        if first:
            duty_cycle = 2 + (angle / 18)
            self.pwm.ChangeDutyCycle(duty_cycle)
            sleep(0.5)
        else:
            duty_cycle = 2 + (self.angle / 18)
            duty_cycle_step = (angle - self.angle) / 18
            for i in range(abs(angle - self.angle)):
                duty_cycle += duty_cycle_step
                self.pwm.ChangeDutyCycle(duty_cycle)
                sleep((100 - self.speed) / (600*self.speed))

        self.angle = angle
        self.pwm.ChangeDutyCycle(0)


    def open_cover(self, first=False):
        self.set_angle(settings.open_angle, first)
        self.cover_opened = True
        log.info("Cover opened")


    def close_cover(self, first=False):
        self.set_angle(settings.close_angle, first)
        self.cover_opened = False
        log.info("Cover closed")
