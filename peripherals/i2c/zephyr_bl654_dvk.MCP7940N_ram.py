# https://www.mikroe.com/temp-hum-4-click
# https://download.mikroe.com/documents/datasheets/hdc1010.pdf
#
# Note: spi0 and i2c0 cannot be enabled on BL654 at the same time
# (controlled by dts/overlay)
#
from machine import I2C
import time

# Setup the I2C
addr = 0x6f
i2c = I2C("i2c@40003000", addr)

# Read battery backed RAM @ address 0x20
i2c.write_read(b"\x20", 4)
# Write it
buf = b"\x20\x12\x34\x56\x78"
i2c.write(buf)
# Read it back after reading different location
time.sleep(1)
junk = i2c.write_read(b"\x24", 4)
read = i2c.write_read(b"\x20", 4)
assert (read == buf[-4:])
