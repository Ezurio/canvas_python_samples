app_id='xbit_bt610_gpio'
app_ver='0.1.0'

from machine import Pin

# Pin identified by gpio-dynamic label (device tree)
led1 = Pin("LED1", Pin.OUT, 0)
led1.off()

# Pin identified by gpio-dynamic label (device tree)
led2 = Pin("LED2", Pin.OUT, 0)
led2.off()

def sw2_changed(v:int):
    print("SW2", v)
    led1.toggle()

def sw3_changed(v:int):
    print("SW3", v)
    led1.toggle()

def mag_changed(v:int):
    if v == 0:
        print("magnet near")
        led2.on()
    else:
        print("magnet far")
        led2.off()

def din1_changed(v:int):
    print("DIN1", v)

sw2 = Pin("BUTTON 1", Pin.IN, Pin.PULL_UP)
sw3 = Pin("BUTTON2", Pin.IN, Pin.PULL_UP)
sw2.configure_event(sw2_changed, Pin.EVENT_BOTH)
sw3.configure_event(sw3_changed, Pin.EVENT_BOTH)

mag = Pin("MAG1", Pin.IN, Pin.PULL_NONE)
mag.configure_event(mag_changed, Pin.EVENT_BOTH)

din1_en = Pin("Digital Input 1 Enable", Pin.OUT, 0)
din1_en.on()

din1 = Pin("Digital Input 1", Pin.IN, Pin.PULL_NONE)
din1.configure_event(din1_changed, Pin.EVENT_BOTH)
