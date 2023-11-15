from machine import Pin
import time

count = 0


def foo(v: int):
    global count
    count += 1
    print(count)


# PA08 is the LED
p = Pin("LED", Pin.OUT, Pin.PULL_NONE)
# Output register can be read on Lyra
# but it may not reflect board state if a peripheral is controlling pin
p.on()
assert (p.value() == 1)
p.off()
assert (p.value() == 0)
# Blink LED 5 times
for _ in range(0, 10):
    p.toggle()
    time.sleep_ms(100)

i = Pin("BTN0", Pin.IN, 0)
i.configure_event(foo, Pin.EVENT_FALLING)
i.value()
assert (i.value() == 1)
print("Press the button")
time.sleep(2)
assert (i.value() == 0)
