"""
	Simple example of using the TempAndHum Click wrapper class
	TempAndHumClick.py, TempAndHumFloat.py and TempAndHumInt.py must be
	present on the Canvas device file system.
	Lyra and SERA boards are supported.
	Float and Int selection is automatic based on the board type.
"""
import os
from TempAndHumClick import TempAndHumClick18
#from TempAndHumClick import TempAndHumClick4

board = os.uname().machine
th_click = None
if "LYRA_24" in board:
	i2c_setup = ("I2C0", 'PD03', 'PD02')
	th_click = TempAndHumClick18(i2c_setup)
	#th_click = TempAndHumClick4(i2c_setup, "PC06", "PC03", 0x42)
else:
	ad0 = ("gpio@50000000", 31)
	ad1 = ("gpio@50000000", 20)
	i2c_setup = "i2c@40003000"
	th_click = TempAndHumClick18(i2c_setup)
	#th_click = TempAndHumClick4(i2c_setup, ad0, ad1, 0x40)

th_click.set_resolution(14,14)

th_click.get_info()

th_click.get_temp_c()

th_click.get_status()

th_click.get_humidity()

th_click.get_status()

th_click.get_temp_f()

th_click.get_status()

th_click.get_temp_c_and_humidity()

th_click.get_status()

th_click.get_temp_f_and_humidity()

th_click.get_status()

