from machine import Pin
from board import Board

class Led:
    # g = Pin(('gpio@50000000',22),Pin.OUT, Pin.PULL_NONE)
    GREEN_LED_GPIO_DEVICE = "gpio@50000000"
    GREEN_LED_GPIO_BANK = 0
    GREEN_LED_GPIO_PIN = 22
    RED_LED_GPIO_DEVICE = "gpio@50000000"
    RED_LED_GPIO_BANK = 0
    RED_LED_GPIO_PIN = 20
    green_led_pin = None
    red_led_pin = None

    # Default to disable the LEDs, call enable() to enable them
    def __init__(self):
        # Default to disable the LEDs
        self.disable()

    # Initialize the state of the green and red LEDs
    def enable(self):
        self.green_led_pin = Pin((self.GREEN_LED_GPIO_DEVICE, self.GREEN_LED_GPIO_PIN), Pin.OUT, Pin.PULL_NONE)
        self.red_led_pin = Pin((self.RED_LED_GPIO_DEVICE, self.RED_LED_GPIO_PIN), Pin.OUT, Pin.PULL_NONE)
        
    def green_on(self):
        if self.green_led_pin is not None:
            self.green_led_pin.on()
    
    def green_off(self):
        if self.green_led_pin is not None:
            self.green_led_pin.off()

    def red_on(self):
        if self.red_led_pin is not None:
            self.red_led_pin.on()
    
    def red_off(self):
        if self.red_led_pin is not None:
            self.red_led_pin.off()

    # Disconnect the pins to the LEDs
    def disable(self):
        self.green_led_pin = Board.disconnect_pin(self.GREEN_LED_GPIO_BANK, self.GREEN_LED_GPIO_PIN)
        self.red_led_pin = Board.disconnect_pin(self.RED_LED_GPIO_BANK, self.RED_LED_GPIO_PIN)
