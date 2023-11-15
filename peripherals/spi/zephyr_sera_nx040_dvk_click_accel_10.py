# https://www.mikroe.com/accel-10-click
# https://download.mikroe.com/documents/datasheets/lis2dw12_datasheet.pdf
# 
# Read identity register
#
from machine import Pin
from machine import SPI

WHO_AM_I_VALUE = b"\x44"

# Configure interrupt pins as inputs
int1 = Pin("GPIO3", Pin.IN, Pin.PULL_NONE)
int2 = Pin("GPIO2", Pin.IN, Pin.PULL_NONE)

# When gpio-dynamic is used, polarity must be specified in device tree
spi = SPI("spi@40023000", Pin("SPI_CS", Pin.OUT, Pin.PULL_NONE))
spi.configure(1000000, 1, 1, SPI.MSB)

# Read WHO_AM_I @ 0x0f | 0x80 (read mask)
# ~ 8 us for chip select
rdata = spi.transceive(b"\x8f\x00")
assert (WHO_AM_I_VALUE == rdata[-1:])
