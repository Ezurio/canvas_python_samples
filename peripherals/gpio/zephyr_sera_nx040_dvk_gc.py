# Garbage collection/heap test
from machine import Pin
import gc
import time

HALF_PERIOD_MS = 10

# Saleae or X can be used to count edges
# This value was used with MicroPython heap size of 4000
LOOP_COUNT = 1000

# mem free seems to allocate memory itself
# however, in a loop by itself the printed value was constant
gc.collect()
gc.mem_alloc()
gc.mem_free()


def allocate_loop():
    """
    Allocate a pin over and over
    """
    p = Pin(("gpio@50000000", 30), Pin.OUT, 0)
    for i in range(0, LOOP_COUNT):
        assert (p is not None)
        p.on()
        time.sleep_ms(HALF_PERIOD_MS)
        p.off()
        time.sleep_ms(HALF_PERIOD_MS)
        print(gc.mem_free())
        p = Pin(("gpio@50000000", 30), Pin.OUT, 0)


def reconfigure_loop():
    """
    Reconfigure a pin multiple times
    """
    b = Pin(("gpio@50000000", 30), Pin.OUT, 0)
    for i in range(0, LOOP_COUNT):
        assert (b is not None)
        b.on()
        time.sleep_ms(HALF_PERIOD_MS)
        b.off()
        time.sleep_ms(HALF_PERIOD_MS)
        print(gc.mem_free())
        b.reconfigure(("gpio@50000000", 30), Pin.OUT, 0)


allocate_loop()
reconfigure_loop()
