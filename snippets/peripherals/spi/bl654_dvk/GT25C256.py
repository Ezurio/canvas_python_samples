# https://www.giantec-semi.com/juchen1123/uploads/pdf/GT25C256_DS_Cu.pdf
#
# Write and read 4 bytes.
#
# Address is 16-bits
# Size of 32 KBytes
#
# Note: spi0 and i2c0 cannot be enabled on BL654 at the same time
# (controlled by dts/overlay)
#
from machine import Pin
from machine import SPI
from time import sleep_ms

WRITE_DURATION_MS = 10

WREN = b"\x06"
WRDI = b"\x04"
RDSR = b"\x05"
WRSR = b"\x01"
READ = b"\x03"
WRITE = b"\x02"

addr = b"\x00\x00"
data = b"\x12\x34\x56\x78"

# Setup peripheral
spi = SPI("spi@40003000", Pin("SPI_CS", Pin.OUT, Pin.PULL_NONE))

# Write data, wait, read status, disable writing
spi.transceive(WREN)
spi.transceive(WRITE + addr + data)
sleep_ms(WRITE_DURATION_MS)
spi.transceive(RDSR)
spi.transceive(WRDI)

# Read data
# Ideally, perform this step after a power cycle
dummy = b"\x00\x00\x00\x00"
rdata = spi.transceive(READ + addr + dummy)
assert (data == rdata[-4:])
