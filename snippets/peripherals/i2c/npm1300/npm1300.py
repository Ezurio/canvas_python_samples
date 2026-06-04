import machine


class NPM1300:
    def __init__(self, device='mikrobus_i2c', address=0x6B):
        self.i2c = machine.I2C(device, address)

    def set_current_limit(self, limit_ma):
        # Convert current limit in mA to register value (assuming 100mA steps)
        ilim_value = limit_ma // 100
        if ilim_value < 0 or ilim_value > 0x0F:
            raise ValueError("Current limit must be between 0 and 1500 mA")
        # Write the ILIM value to the appropriate register (base 0x02, offset 0x01)
        self.i2c.write(bytes([0x02, 0x01, ilim_value]))
        # Trigger ILIMUPDATE by writing to the same register with a specific command
        self.i2c.write(bytes([0x02, 0x00, 0x01]))

    def read_current_limit(self):
        # Read the ILIM register value (base 0x02, offset 0x01)
        data = self.i2c.write_read(bytes([0x02, 0x01]), 1)
        # Convert the register value to current limit in mA
        ilim_value = data[0] & 0x0F
        current_limit_ma = ilim_value * 100
        return current_limit_ma
