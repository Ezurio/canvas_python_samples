from machine import Pin

# GPIO3 described by device name (GPIO port) and pin number
p = Pin(("gpio@50000000", 30), Pin.OUT, 0)
p.on()
