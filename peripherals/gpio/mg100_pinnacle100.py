from machine import Pin
import canvas
import os


if "mg100" == os.uname().machine:
    RED_LED = "LED_RED"
    BLUE_LED = "LED_BLUE"
    GREEN_LED = "LED_GREEN"
    BUTTON = "BUTTON"
elif "pinnacle_100_dvk" == os.uname().machine:
    RED_LED = "LED1"
    BLUE_LED = "LED2"
    GREEN_LED = "LED3"
    BUTTON = "BUTTON1"
else:
    raise Exception(
        "This script is not compatible with this board {}".format(os.uname().machine))

B_LED_STATE = 0
G_LED_STATE = 1
R_LED_STATE = 2

BUTTON_DEBOUNCE_TIME_MS = 50


def debounce_callback(event):
    global r_led, b_led, g_led, state, button
    if button.value() == 1:
        # The button is not pressed, don't do anything now.
        return

    # Walk through the states of the LEDs
    if state == B_LED_STATE:
        b_led.on()
        r_led.off()
        state = G_LED_STATE
        return
    elif state == G_LED_STATE:
        g_led.on()
        b_led.off()
        state = R_LED_STATE
        return
    elif state == R_LED_STATE:
        r_led.on()
        g_led.off()
        state = B_LED_STATE
        return


def button_event(e: int):
    global debounce_timer
    debounce_timer.restart()


state = B_LED_STATE
# Configure the GPIO pins as outputs for the LEDs
r_led = Pin(RED_LED, Pin.OUT, 0)
b_led = Pin(BLUE_LED, Pin.OUT, 0)
g_led = Pin(GREEN_LED, Pin.OUT, 0)
# Turn off all the LEDs
r_led.off()
b_led.off()
g_led.off()
# Configure the GPIO pin as an input for the button
button = Pin(BUTTON, Pin.IN, Pin.PULL_UP)

# Initialise a debounce timer. This timer is used to debounce the button.
debounce_timer = canvas.Timer(
    BUTTON_DEBOUNCE_TIME_MS, False, debounce_callback, None)
# Configure the button to call the button_event function when the button is pressed.
button.configure_event(button_event, Pin.EVENT_FALLING)
