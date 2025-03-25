import RPi.GPIO as GPIO
from settings.config import *


class CameraModeController:
    """Controls camera day/night mode by managing the IR filter"""
    
    def __init__(self):
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM) # we always use BCM to prevent conflicts

        self.camera_mode_pin = settings.camera_mode_pin
        self._current_state = None

        if settings.camera_mode == "auto":
            log.info(f"Camera mode set to auto (controlled by light sensor)")
            GPIO.setup(self.camera_mode_pin, GPIO.IN)

        elif settings.camera_mode == "day":
            GPIO.setup(self.camera_mode_pin, GPIO.OUT)
            self.set_mode("DAY")
        elif settings.camera_mode == "night":
            GPIO.setup(self.camera_mode_pin, GPIO.OUT)
            self.set_mode("NIGHT")

        self.update_current_state()


    def update_current_state(self, channel=None):
        self._current_state = "NIGHT" if GPIO.input(self.camera_mode_pin) else "DAY"
        log.debug(f"Camera mode: {self._current_state}")
               

    @property
    def current_state(self):
        self.update_current_state()
        return self._current_state


    def set_mode(self, mode):
        try:
            if mode == "DAY":
                GPIO.output(self.camera_mode_pin, GPIO.LOW)
            else:
                GPIO.output(self.camera_mode_pin, GPIO.HIGH)
        except Exception as e:
            log.error(f"Failed to set camera mode: {e}", exc_info=True)


    def cleanup(self):
        GPIO.cleanup(self.camera_mode_pin)
