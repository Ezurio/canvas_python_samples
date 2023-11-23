import os
import time
from AccelClick import Accel10Click

board = os.uname().machine
th_click = None
i2c_setup = None
if "LYRA_24" in board:
	i2c_setup = ("I2C0", 'PD03', 'PD02')
else:
	i2c_setup = "i2c@40003000"

accel = Accel10Click(i2c_setup)
accel.set_mode(Accel10Click.SINGLE_SHOT_MODE, Accel10Click.LOW_POWER_DR_12_5HZ)

while True:
	print("Raw: ", accel.get_raw_values())
	print("Signed: ", accel.get_signed_values())
	print("Difference: ", accel.get_difference())
	time.sleep_ms(500)

