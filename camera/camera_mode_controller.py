from gpiozero import DigitalInputDevice, DigitalOutputDevice
from settings.config import *


class CameraModeController:
    """Controls camera day/night mode by managing the IR filter"""
    
    def __init__(self):

        self.camera_mode_pin = settings.camera_mode_pin
        self._current_state = None
        self._pin_device = None

        if settings.camera_mode == "auto":
            log.info(f"Camera mode set to auto (controlled by light sensor)")
            self._pin_device = DigitalInputDevice(
                pin=self.camera_mode_pin,
                pull_up=True,
                bounce_time=0.5
            )
            self._pin_device.when_activated = self.update_current_state
            self._pin_device.when_deactivated = self.update_current_state

        elif settings.camera_mode == "day":
            self.set_mode("DAY")
        elif settings.camera_mode == "night":
            self.set_mode("NIGHT")

        self.update_current_state()


    def update_current_state(self, channel=None):
        self._current_state = "DAY" if self._pin_device.value else "NIGHT"
        log.debug(f"Camera mode: {self._current_state}")
               

    @property
    def current_state(self):
        return self._current_state


    def set_mode(self, mode):
        try:
            if self._pin_device is None or not isinstance(self._pin_device, DigitalOutputDevice):
                if self._pin_device:
                    self._pin_device.close()
                self._pin_device = DigitalOutputDevice(self.camera_mode_pin)
            if mode == "DAY":
                self._pin_device.off()
            else:
                self._pin_device.on()
        except Exception as e:
            log.error(f"Failed to set camera mode: {e}", exc_info=True)


    def cleanup(self):
        if self._pin_device:
            self._pin_device.close()
