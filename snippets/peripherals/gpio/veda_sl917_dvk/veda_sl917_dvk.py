from machine import Pin
import time

def button0_pressed_cb(pin: Pin):
    """Callback function for button press event."""
    print("BTN0 pressed, toggling LED0")  # Print message when button is pressed
    led0.toggle()  # Toggle LED state

def button1_pressed_cb(pin: Pin):
    """Callback function for button press event."""
    print("BTN1 pressed, toggling LED1")  # Print message when button is pressed
    led1.toggle()  # Toggle LED state

led0 = Pin("LED0", Pin.OUT, Pin.PULL_NONE)  # GPIO pin for LED0
led1 = Pin("LED1", Pin.OUT, Pin.PULL_NONE)  # GPIO pin for LED1
button0 = Pin("BUTTON0", Pin.IN, Pin.PULL_NONE)  # GPIO pin for button0
button0.configure_event(button0_pressed_cb, Pin.EVENT_FALLING)  # Configure button0 event
button1 = Pin("BUTTON1", Pin.IN, Pin.PULL_UP)  # GPIO pin for button1
button1.configure_event(button1_pressed_cb, Pin.EVENT_FALLING)  # Configure button1 event

# Blink 5 times
for _ in range(5):
    led0.on()  # Turn on LED0
    led1.off()  # Turn off LED1
    time.sleep_ms(100)  # Wait for 0.1 seconds
    led0.off()  # Turn off LED0
    led1.on()  # Turn on LED1
    time.sleep_ms(100)  # Wait for 0.1 seconds

led1.off()

