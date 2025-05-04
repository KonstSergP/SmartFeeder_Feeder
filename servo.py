import RPi.GPIO as GPIO
from time import sleep

from settings.config import *


class Servo:
    """Controls the servo motor that operates the feeder cover.\n"""
    def __init__(self) -> None:
        self.pin = settings.servo_pin

        speed = {"slow": 0.07, "medium": 0.055, "fast": 0.045}
        self.speed = speed[settings.servo_speed]
        self.angle = None
        self.cover_opened = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)

        self.close_cover(True)


    def cleanup(self) -> None:
        """
        Release resources of GPIO.\n
        Must be called when shutting down to prevent issues and to free GPIO resources.
        """
        self.pwm.stop()
        GPIO.cleanup(self.pin)


    def set_angle(self, angle: int, first: bool=False) -> None:
        """
        Set the servo to a specific angle.\n
        For the first movement, the servo moves directly to the position.
        For subsequent movements, the servo moves step by step for smoother motion.\n
        Args:
            angle: Target angle (0-180 degrees)
            first: Whether this is the first movement (True) or a regular movement (False)
        """
        if first:
            duty_cycle = 2.5 + (angle / 18)
            self.pwm.ChangeDutyCycle(duty_cycle)
            sleep(0.5)
            self.angle = angle
        else:
            duty_cycle = 2 + (self.angle / 18)
            step = 5 if angle > self.angle else -5
            while self.angle != angle:
                self.pwm.ChangeDutyCycle(2.5 + (self.angle / 18))
                sleep(self.speed)
                self.angle += step

        self.pwm.ChangeDutyCycle(0)


    def open_cover(self, first: bool=False) -> None:
        self.set_angle(settings.open_angle, first)
        self.cover_opened = True
        log.info("Cover opened")


    def close_cover(self, first: bool=False) -> None:
        self.set_angle(settings.close_angle, first)
        self.cover_opened = False
        log.info("Cover closed")
