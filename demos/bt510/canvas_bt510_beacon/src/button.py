from machine import Pin
from board import Board

class Button:
    BUTTON_GPIO_DEVICE = "gpio@50000300"
    BUTTON_GPIO_BANK = 1
    BUTTON_GPIO_PIN = 10
    button_pin = None

    # Default to disabled, call enable() to setup the button I/O
    def __init__(self):
        self.disable()
        
    # Setup the pushbutton GPIO pin
    def enable(self):
        self.button_pin = Pin((self.BUTTON_GPIO_DEVICE, self.BUTTON_GPIO_PIN), Pin.IN, Pin.PULL_UP)

    # Disconnect the pin to the button
    def disable(self):
        self.button_pin = Board.disconnect_pin(self.BUTTON_GPIO_BANK, self.BUTTON_GPIO_PIN)

    # Return True if the button is pressed, False otherwise
    def is_pressed(self):
        if self.button_pin is None:
            return False
        return self.button_pin.value() == 0

    # Configure an event when the button is pressed or released
    def on_change(self, callback):
        self.button_pin.configure_event(callback, Pin.EVENT_BOTH)
