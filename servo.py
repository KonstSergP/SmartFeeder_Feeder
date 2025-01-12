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
        pass
        self.pwm.stop()
        GPIO.cleanup()

    def open_cover(self):
        self.set_angle(Config.OPEN_ANGLE)
        self.cover_opened = True
        log.info("Cover opened")
    
    def close_cover(self):
        self.set_angle(Config.CLOSE_ANGLE)
        self.cover_opened = False
        log.info("Cover closed")
