import sys
from machine import Pin
from machine import I2C

class TemperatureSensor:
    TEMP_SENSOR_ADDRESS = 0x40
    TEMP_SENSOR_BUS_DEVICE = "i2c@40003000"
    temp_sensor = None
    temp_sample = None
    temp_status = None

    def __init__(self):
        self.temp_sensor = I2C(self.TEMP_SENSOR_BUS_DEVICE, self.TEMP_SENSOR_ADDRESS)
        self.disable()

    def get_temperature_string(self):
        self.temp_sample = self.temp_sensor.write_read(b"\xe3", 2)
        # Use formula from Si705x datasheet to convert sample to temperature
        # adapted for integer divide. (floating point unavailable in BT510 micropython build)
        temp_celsius_x100 = (int.from_bytes(self.temp_sample, 'big') * 17572 // 65536) - 4685
        # Create a string with the temperature in Celsius
        temp_celsius_string_x100 = str(temp_celsius_x100)
        temp_celsius_string = temp_celsius_string_x100[0:-2] + '.' +  temp_celsius_string_x100[-2:len(temp_celsius_string_x100)]
        return temp_celsius_string
    
    def get_status_bytes(self):
        self.temp_status = self.temp_sensor.write_read(b"\xe7", 1)
        return self.temp_status
    
    def get_battery_ok(self):
        self.get_status_bytes()
        if (int.from_bytes(self.temp_status, sys.byteorder) & 0x40) == 0x40:
            return False
        return True

    def enable(self):
        # send command to wake up temperature sensor
        self.get_temperature_string()

    def disable(self):
        # Do nothing, temperature sensor automatically powers down
        pass
