# https://www.mikroe.com/weather-click
# https://download.mikroe.com/documents/datasheets/BME280.pdf
#
# Read identity register
# Specify pin details in init
# Test SPI mode reconfiguration
#
from machine import SPI

ID_REG = b"\xD0"
ID_VAL = b"\x60"
dummy = b"\x00"

spi = SPI("spi@40023000", ("gpio@50000000", 20, SPI.CS_ACTIVE_LOW))

# Read ID register
rdata = spi.transceive(ID_REG + dummy)
assert (ID_VAL == rdata[-1:])

# Change configuration and make sure it works
# Currently this must be verified using scope.
# (part supports both modes).
spi.configure(1000000, 1, 1, SPI.MSB)
rdata = spi.transceive(ID_REG + dummy)
assert (ID_VAL == rdata[-1:])

# Back to original
spi.configure(1000000, 0, 0, SPI.MSB)
rdata = spi.transceive(ID_REG + dummy)
assert (ID_VAL == rdata[-1:])
