# https://www.mikroe.com/accel-10-click
# https://download.mikroe.com/documents/datasheets/lis2dw12_datasheet.pdf
#
# Read identity register
#
from machine import Pin
from machine import SPI

WHO_AM_I_VALUE = b"\x44"

# Configure interrupt pins as inputs
int1 = Pin("GPIO2", Pin.IN, Pin.PULL_NONE)
int2 = Pin("GPIO2", Pin.IN, Pin.PULL_NONE)

# Manually control chip select (active low)
csn = Pin(("gpio@50000000", 20), Pin.OUT, Pin.PULL_NONE)
csn.high()

# Setup peripheral and modify clock polarity and phase from default
spi = SPI("spi@40023000", None)
spi.configure(1000000, 1, 1, SPI.MSB)

# Do a dummy cycle to make sure clock line is in the correct state
# (high when chip select goes low)
junk = spi.transceive(b"\x8f\x00")

# Read WHO_AM_I @ 0x0f | 0x80 (read mask)
csn.low()
# ~2.5 ms from cs low to first clock edge
rdata = spi.transceive(b"\x8f\x00")
csn.high()
assert (WHO_AM_I_VALUE == rdata[-1:])
