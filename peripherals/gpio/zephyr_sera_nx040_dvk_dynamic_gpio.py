from machine import Pin
from time import sleep

# Pin identified by gpio-dynamic label (device tree)
p = Pin("GPIO3", Pin.OUT, 0)
p.off()

def foo(v:int):
    print(v)

# 3 and 1 must be connected
i = Pin("GPIO1", Pin.IN, Pin.PULL_NONE)
i.configure_event(foo, Pin.EVENT_BOTH)

p.on()
sleep(1)

p.off()
sleep(1)

i.configure_event(None, Pin.EVENT_NONE)
sleep(1)

p.on()
sleep(1)

i.configure_event(foo, Pin.EVENT_FALLING)
p.off()
