from machine import Pin
import time

led0 = Pin("LED", Pin.OUT, Pin.PULL_NONE)  # GPIO pin for LED

# Blink 5 times
for _ in range(5):
    led0.on()  # Turn on LED
    time.sleep_ms(100)  # Wait for 0.1 seconds
    led0.off()  # Turn off LED
    time.sleep_ms(100)  # Wait for 0.1 seconds

def button_pressed_cb(pin: Pin):
    """Callback function for button press event."""
    print("Button pressed, toggling LED")  # Print message when button is pressed
    led0.toggle()  # Toggle LED state

button0 = Pin("BTN0", Pin.IN, Pin.PULL_NONE)  # GPIO pin for button
button0.configure_event(button_pressed_cb, Pin.EVENT_FALLING)  # Configure button event

