from machine import Pin
from board import Board

class OpenCloseSensor:
    OPEN_CLOSE_GPIO_DEVICE = "gpio@50000300"
    OPEN_CLOSE_GPIO_BANK = 1
    OPEN_CLOSE_GPIO_PIN = 14
    open_close_pin = None

    # Default to disabled, call enable() to enable
    def __init__(self):
        self.disable()
    
    # Enable the open/close sensor
    def enable(self):
        self.open_close_pin = Pin((self.OPEN_CLOSE_GPIO_DEVICE, self.OPEN_CLOSE_GPIO_PIN), Pin.IN, Pin.PULL_NONE)

    # Disable the open/close sensor
    def disable(self):
        self.open_close_pin = Board.disconnect_pin(self.OPEN_CLOSE_GPIO_BANK, self.OPEN_CLOSE_GPIO_PIN)
    
    # Check if the door is open (magnet not present)
    def is_open(self):
        if self.open_close_pin is None:
            return False
        return self.open_close_pin.value() == 1
    
    # Check if the door is closed (magnet is present)
    def is_closed(self):
        if self.open_close_pin is None:
            return False
        return self.open_close_pin.value() == 0
    
    # Configure an event when the button is pressed or released
    def on_change(self, callback):
        self.open_close_pin.configure_event(callback, Pin.EVENT_BOTH)
