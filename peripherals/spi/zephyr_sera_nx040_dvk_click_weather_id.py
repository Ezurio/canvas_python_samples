# https://www.mikroe.com/weather-click
# https://download.mikroe.com/documents/datasheets/BME280.pdf
#
# Read identity register
#
from machine import Pin
from machine import SPI

ID_REG = b"\xD0"
ID_VAL = b"\x60"
dummy = b"\x00"

# When gpio-dynamic is used, polarity must be specified in device tree
spi = SPI("spi@40023000", Pin("SPI_CS", Pin.OUT, Pin.PULL_NONE))

# Read ID register
rdata = spi.transceive(ID_REG + dummy)
assert (ID_VAL == rdata[-1:])
