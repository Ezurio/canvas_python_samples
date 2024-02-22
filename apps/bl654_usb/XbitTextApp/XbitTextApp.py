from XbitTextService import XbitTextService
from AppBanner import Banner
from machine import Pin
import canvas
import os

app_id = "Xbit Text Client"
app_ver = "0.3.0"

#--------------------------------------
# Application script
#--------------------------------------

board = os.uname().machine
led_state = False
led = None

def send(text):
    global xbitTextClient
    xbitTextClient.send(text)

def cb_connected():
    print('Type "send(\'message\')" to send a message')

def cb_message_received(message):
    print("Message received: " + message)

def cb_led_timer(event):
    global board
    global led_state
    global led
    if "sera_nx040_dvk" in board and led is not None:
        if led_state:
            led.set(0, 0x00000A)
        else:
            led.set(0, 0x000000)
        led_state = not led_state
    elif "bl654_usb" in board and led is not None:
        led.toggle()

# Display application banner
Banner.printAppBanner(app_id, app_ver)

# Start a timer to blink an LED indicating the script is running
if "sera_nx040_dvk" in board:
    led = canvas.LEDStrip("", 1)
elif "bl654_usb" in board:
    led = Pin('LED1', Pin.OUT, 0)

timer = canvas.Timer(500, True, cb_led_timer, None)
timer.start()

# Instantiate and start the XbitTextService
xbitTextClient = XbitTextService(cb_connected, cb_message_received)
xbitTextClient.start()
xbitTextClient.printMyName()
