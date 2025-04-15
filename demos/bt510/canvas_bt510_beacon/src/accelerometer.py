from machine import Pin
from machine import I2C
import struct

class Accelerometer:
    ACCELEROMETER_ADDRESS = 0x18
    ACCELEROMETER_BUS_DEVICE = "i2c@40003000"
    accelerometer = None
    accel_sample = None

    CMD_ACCELEROMETER_ON = b"\xa0\x2f"
    CMD_ACCELEROMETER_OFF = b"\xa0\x08"


    def __init__(self):
        self.accelerometer = I2C(self.ACCELEROMETER_BUS_DEVICE, self.ACCELEROMETER_ADDRESS)
        # Disconnect the SA0 pin
        self.accelerometer.write(b"\x1e\x90")
        self.disable()
    
    def disable(self):
        # Power down the accelerometer
        self.accelerometer.write(self.CMD_ACCELEROMETER_OFF)
    
    def enable(self):
        # Power up the accelerometer
        self.accelerometer.write(self.CMD_ACCELEROMETER_ON)

    # NOTE: performs a 16 bit read but the accelerometer is in low power mode
    # so only returns signed 8 bit values. 
    def read_bytes(self):
        self.accel_sample = self.accelerometer.write_read(b"\xa8", 6)
        return struct.unpack("xbxbxb", self.accel_sample)
    
    def get_acceleration_string(self):
        x, y, z = self.read_bytes()
        return "X:" + str(x) + ", Y:" + str(y) + ", Z:" + str(z)

