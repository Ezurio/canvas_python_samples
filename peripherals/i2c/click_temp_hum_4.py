# https://www.mikroe.com/temp-hum-4-click
# https://download.mikroe.com/documents/datasheets/hdc1010.pdf
from machine import Pin
from machine import I2C
import os
import time

MAX_CONVERSION_TIME_MS = 28


# Floating point not supported on NX040
def convert_temp_c(raw):
    return (raw * 165 // 65536) - 40


def convert_temp_f(raw):
    return convert_temp_c(raw) * 9 // 5 + 32


def convert_humidity(raw):
    """Returns Relative Humidity in Percent"""
    return raw * 100 // 65536


def drdy_interrupt(v: int):
    print("i2c data ready\n")


# The API is used differently with different operating systems
board = os.uname().machine
if "LYRA_24" in board:
    lyra24 = True
    AD0 = "PC06"
    AD1 = "PC03"
    DRDY_N = "PB03"
    I2C_DEV = ("I2C0", "PD03", "PD02")
else:
    lyra24 = False
    AD0 = ("gpio@50000000", 31)
    AD1 = ("gpio@50000000", 20)
    DRDY_N = ("gpio@50000000", 29)
    I2C_DEV = "i2c@40003000"

# Setup the I2C
addr = 0x40
i2c = I2C(I2C_DEV, addr)

# Open drain output of HDC1010 must be pulled up.
drdy_n = Pin(DRDY_N, Pin.IN, Pin.PULL_UP)
drdy_n.configure_event(drdy_interrupt, Pin.EVENT_FALLING)
time.sleep(1)

# Set 2 configurable address bits (RST and CS mikroBus lines)
Pin(AD0, Pin.OUT, Pin.PULL_NONE).off()
if lyra24:
    # If the SPI peripheral is enabled with chip select control,
    # then ad1 can't be set to 0.
    # There currently isn't a way to detect this condition (without a scope).
    i2c.set_address(0x42)
    # If CS is configured for the SPI bus, then this won't do anything.
    Pin(AD1, Pin.OUT, Pin.PULL_NONE).on()
else:
    Pin(AD1, Pin.OUT, Pin.PULL_NONE).off()


# Read the manufacturer ID (TI) and device ID (0x1000)
# burst not supported
result = i2c.write_read(b"\xFE", 2)
assert result == b"\x54\x49"
assert result == b"TI"
result = i2c.write_read(b"\xFF", 2)
assert result == b"\x10\x00"

# Configure for 14-bit temperature and humidity
i2c.write("\x02\x10\x00")

# Start conversion, wait, and read result
i2c.write("\x00")
time.sleep_ms(MAX_CONVERSION_TIME_MS)
# If the results aren't ready, then 4 bytes won't be returned.
result = i2c.read(4)
assert len(result) == 4

# Convert results
temp_raw = int.from_bytes(result[:2], "big")
hum_raw = int.from_bytes(result[-2:], "big")
convert_temp_c(temp_raw)
convert_humidity(hum_raw)
