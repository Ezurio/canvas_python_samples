import time

class TempHum4Click:

    def __init__(self, i2c):
        self.i2c = i2c
        self.MAX_CONVERSION_TIME_MS = 40
    
    def is_present(self):
        mfr = self.i2c.write_read(b"\xFE", 2)
        if mfr != b'TI':
            return False
        deviceid = self.i2c.write_read(b"\xFF", 2)
        if deviceid != b'\x10\x00':
            return False
        return True

    def configure(self):
        # Configure for 14-bit temperature and humidity
        self.i2c.write("\x02\x10\x00")

    def read(self):
        # Start conversion, wait, and read result
        self.i2c.write("\x00")
        time.sleep_ms(self.MAX_CONVERSION_TIME_MS)
        # If the results aren't ready, then 4 bytes won't be returned.
        result = self.i2c.read(4)
        data = {}
        if len(result) == 4:
            temp_raw = int.from_bytes(result[:2], "big")
            data['temperature'] = ((temp_raw / 65536.0) * 165.0) - 40.0
            hum_raw = int.from_bytes(result[-2:], "big")
            data['humidity'] = (hum_raw / 65536.0) * 100.0
        else:
            data = None
        return data

