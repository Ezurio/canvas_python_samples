# https://www.mikroe.com/weather-click
# https://download.mikroe.com/documents/datasheets/BME280.pdf
#
# Read identity register
#
from machine import SPI
from machine import Pin

ID_REG = b"\xD0"
ID_VAL = b"\x60"
dummy = b"\x00"

# Read ID register
spi = SPI(("USART0", "PC02", "PC04", "PC05"), ("PC03", SPI.CS_ACTIVE_LOW))
rdata = spi.transceive(ID_REG + dummy)
assert ID_VAL == rdata[-1:]

# Create another configuration with 2M, opposite phase and polarity, and pin
#
# Note: If chip select is configured for use by SPI peripheral in firmware, 
# then Pin can be used to create SPI instance but
# high and low won't work even though .value() is correct.
#
cs = Pin("PC03", Pin.OUT, Pin.PULL_NONE)
spi2 = SPI(("USART0", "PC02", "PC04", "PC05"), cs)
spi2.configure(2000000, 1, 1, SPI.MSB)
rdata = spi2.transceive(ID_REG + dummy)
assert ID_VAL == rdata[-1:]
