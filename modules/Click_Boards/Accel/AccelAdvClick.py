app_id='global_accel10'
app_ver='1.0.0'

import canvas
import canvas_ble
import time
import os
import binascii
from AccelClick import Accel10Click

ads_started = False
config = { }
board = os.uname().machine

def load_config():
	global config
    	# Set default configuration values
	config["reporting_interval_ms"] = 100
	board = os.uname().machine
	if "LYRA_24" in board:
		config["ble_name"] = "Lyra 24"
	else:
		config["ble_name"] = "Sera NX040"
    	# Load configuration from a file
	try:
		f = open("config.cb", "rb")
	except:
		print("Configuration file not found, saving defaults")
		save_config()
		return
    	# Read the entire file
	cbor = f.read()
	f.close()
	if cbor is None:
		print("Configuration file is empty, saving defaults")
		save_config()
		return
	# Convert CBOR to an object
	config_file = canvas.zcbor_to_obj(cbor)
	if config_file is None:
		print("Configuration is corrupt, saving defaults")
		save_config()
		return
	# Copy the configuration from the file
	for c in config_file:
	        config[c] = config_file[c]


def save_config():
	global config
	config_file = { }
	# Copy config values from the live config object
	config_file["reporting_interval_ms"] = config["reporting_interval_ms"]
	config_file["ble_name"] = config["ble_name"]
	# Convert the configuration to CBOR
	cbor = canvas.zcbor_from_obj(config_file, 0)
	if cbor is None:
		print("Unable to convert configuration to CBOR")
		return
	# Write the CBOR to a file
	f = open("config.cb", "wb")
	if f is None:
		print("Unable to open configuration file")
		return
	size = f.write(cbor)
	f.close()


def init_accel_click():
	global accel
	global board
	th_click = None
	i2c_setup = None
	if "LYRA_24" in board:
		i2c_setup = ("I2C0", 'PD03', 'PD02')
	else:
		i2c_setup = "i2c@40003000"
	accel = Accel10Click(i2c_setup)
	accel.set_mode(Accel10Click.SINGLE_SHOT_MODE, Accel10Click.LOW_POWER_DR_12_5HZ)


def read_accel_forever():
	ctr = 0
	reporting_interval_ms = config["reporting_interval_ms"]
	while True:
		update_ad(b"\x77\x00\xc9\x00" + accel.get_raw_values() + bytes([ctr]))
		ctr = ctr + 1
		ret = time.sleep_ms(reporting_interval_ms)


def init_ble():
	global adv
	global config
	adv = canvas_ble.Advertiser()
	reporting_interval_ms = config["reporting_interval_ms"]
	adv.set_interval(reporting_interval_ms, reporting_interval_ms + 50)
	adv.set_properties(True, True, False)
	adv.clear_buffer(True)
	adv.add_canvas_data(0, 0, True)

def update_ad(arr):
	global adv
	global ads_started
	devid = canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14] + canvas_ble.addr_to_str(canvas_ble.my_addr())[15:17]
	adv.clear_buffer(False)
	adv.add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([0x06]), False)
	adv.add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, config['ble_name'] + '-' + devid, False)
	adv.add_ltv(canvas_ble.AD_TYPE_MANU_SPECIFIC, arr, False)
	if ads_started == False:
		ret = adv.start()
		ads_started = True
	else:
		ret = adv.update()


load_config()
canvas_ble.init()
init_accel_click()
init_ble()
print(' \r\n' + config["ble_name"] +' Accel 10 Click tilt sensor script')
print('--------------------------------------------')
print('Reporting Interval: ' + str(config["reporting_interval_ms"]) + 'ms')
print('Press ctrl-c to interrupt the running script and access the REPL\r\n ')
read_accel_forever()

