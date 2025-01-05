import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)

servo = GPIO.PWM(14, 50)

servo.start(0)

def set_angle(angle):
    angle = angle / 18 + 2
    #GPIO.output(servo, True)
    servo.ChangeDutyCycle(angle)
    time.sleep(1)
    #GPIO.output(False)
    servo.ChangeDutyCycle(0)
    

set_angle(90)
set_angle(45)
set_angle(180)
set_angle(0)

servo.stop()
GPIO.cleanup()
