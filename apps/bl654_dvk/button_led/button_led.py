app_id = 'xbit_bl654_button_led'
app_ver = '1.0.1'

import machine

# callback on button 1 press
led1_on = False
def button1_pressed(val):
    global led1_on
    led1_on = not led1_on
    print('BUTTON1 pressed, LED1', led1_on)
    if led1_on:
        led1.high()
    else:
        led1.low()

# callback on button 2 press
led2_on = False
def button2_pressed(val):
    global led2_on
    led2_on = not led2_on
    print('BUTTON2 pressed, LED2', led2_on)
    if led2_on:
        led2.high()
    else:
        led2.low()

# callback on button 3 press
led3_on = False
def button3_pressed(val):
    global led3_on
    led3_on = not led3_on
    print('BUTTON3 pressed, LED3', led3_on)
    if led3_on:
        led3.high()
    else:
        led3.low()

# callback on button 4 press
led4_on = False
def button4_pressed(val):
    global led4_on
    led4_on = not led4_on
    print('BUTTON4 pressed, LED4', led4_on)
    if led4_on:
        led4.high()
    else:
        led4.low()

# setup GPIO objects for each LED
led1 = machine.Pin('LED1', machine.Pin.OUT, 0)
led2 = machine.Pin('LED2', machine.Pin.OUT, 0)
led3 = machine.Pin('LED3', machine.Pin.OUT, 0)
led4 = machine.Pin('LED4', machine.Pin.OUT, 0)

# setup GPIO objects for each button
button1 = machine.Pin('BUTTON1', machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin('BUTTON2', machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin('BUTTON3', machine.Pin.IN, machine.Pin.PULL_UP)
button4 = machine.Pin('BUTTON4', machine.Pin.IN, machine.Pin.PULL_UP)

# configure button press callback on each button
button1.configure_event(button1_pressed, machine.Pin.EVENT_FALLING)
button2.configure_event(button2_pressed, machine.Pin.EVENT_FALLING)
button3.configure_event(button3_pressed, machine.Pin.EVENT_FALLING)
button4.configure_event(button4_pressed, machine.Pin.EVENT_FALLING)

print(' app_id:', app_id)
print('app_ver:', app_ver)
print('Press a User Button (BUTTON1-BUTTON4) to toggle LEDs (D1-D4)')