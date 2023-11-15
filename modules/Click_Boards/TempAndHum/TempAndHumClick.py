import time
from machine import Pin
from machine import I2C
import os

class TempAndHumClickBase:
	"""
		Abstract base class for TempAndHumClick
	"""
	STATUS_VALID_DATA = 0x00
	STATUS_STALE_DATA = 0x01

	def get_temp_c(self):
		"""
			Abstract method for getting temperature in Celsius
		"""
		pass

	def get_humidity(self):
		"""
			Abstract method for getting humidity
		"""
		pass

	def get_temp_f(self):
		"""
			Abstract method for getting temperature in Fahrenheit
		"""
		pass

	def get_temp_c_and_humidity(self):
		"""
			Abstract method for getting temperature in Celsius and humidity
		"""
		return (self.get_temp_c(), self.get_humidity())

	def get_temp_f_and_humidity(self):
		"""
			Abstract method for getting temperature in Fahrenheit and humidity
		"""
		return (self.get_temp_f(), self.get_humidity())

	def get_info(self) -> (int, int, int):
		"""
			Abstract method for getting the chip ID and config
		"""
		pass

	def set_resolution(self, temp_res: int, hum_res:int):
		"""
			Abstract method for setting the resolution
		"""
		pass

	def get_status(self) -> bool:
		"""
			Abstract method for getting the status as a boolean
		"""
		return self.status

"""
	Autoselect the format module wanted based on the machine type
	Lyra supports float, other boards support int

	if you wish to support int on lyra, remove the auto selection code and
	import the desired format explicitly
"""
if "LYRA_24" in os.uname().machine:
	from TempAndHumFloat import TempAndHumClickFormat
else:
	from TempAndHumInt import TempAndHumClickFormat

class TempAndHumClick18(TempAndHumClickFormat):
	"""
		Concrete class for TempAndHumClick18
	"""
	#
	MASK_STATUS = 0x03
	#
	BIT_MASK_SIGN_14_BIT = 0x1FFF
	BIT_MASK_14_BIT = 0x3FFF
	#
	DIVISOR_TEMP = BIT_MASK_14_BIT
	MULTIPLIER_COEF_TEMP = 165
	ADDITION_COEF_TEMP = -40
	DIVISOR_HUM = BIT_MASK_14_BIT
	MULTIPLIER_COEF_HUM = 100
	#
	SET_DEV_ADDR = 0x44
	FETCH_DELAY_MS = 34
	#
	FETCH = b"\x00"

	def __init__(self, i2c_device:any):
		"""
			Constructor for TempAndHumClick18
			No address is required as the device is fixed
		"""
		self.i2c = I2C(i2c_device, self.SET_DEV_ADDR)

	def get_raw(self):
		"""
			Private method for getting the raw data
		"""
		self.i2c.write(self.FETCH)
		time.sleep_ms(self.FETCH_DELAY_MS)
		buf = self.i2c.read(4)
		self.status = buf[0] >> 6
		self.status &= self.MASK_STATUS
		self.raw_humidity = ((buf[0] << 8) | buf[1]) & self.BIT_MASK_14_BIT
		temp = (((buf[2] << 8) | buf[3]) >> 2) & self.BIT_MASK_14_BIT
		if(temp > self.BIT_MASK_SIGN_14_BIT):
			self.raw_temperature = self.BIT_MASK_SIGN_14_BIT + 1
			self.raw_temperature -= temp
		else:
			self.raw_temperature = temp

	def get_info(self) -> (int, int, int):
		# Renesas chip ID and config only available 10ms from power on
		# this is not feasible at present with the current API
		manufacturer_id = 0
		device_id = 0
		uuid = 0
		return (manufacturer_id, device_id, uuid)

	def set_resolution(self, temp_res: int, hum_res:int):
		# Renesas chip ID and config only available 10ms from power on
		# this is not feasible at present with the current API
		pass

class TempAndHumClick4(TempAndHumClickFormat):
	"""
		Concrete class for TempAndHumClick18
	"""
	#
	DIVISOR_TEMP = 65536
	MULTIPLIER_COEF_TEMP = 165
	ADDITION_COEF_TEMP = -40
	DIVISOR_HUM = 65536
	MULTIPLIER_COEF_HUM = 100
	#
	ADDRESS_MASK_1 = 0x01
	ADDRESS_MASK_2 = 0x02
	#
	HEATER_ENABLED = 0x10
	TEMP_RES_14_BIT = 0x00
	TEMP_RES_11_BIT = 0x04
	HUM_RES_14_BIT = 0x00
	HUM_RES_11_BIT = 0x01
	HUM_RES_8_BIT = 0x02
	#
	FETCH_DELAY_MS = 28
	#
	FETCH = b"\x00"
	MANUFACTURER_ID = b"\xFE"
	DEVICE_ID = b"\xFF"
	CONFIGURATION = b"\x02"

	def __init__(self, i2c_device:any, adr0:str, adr1:str, address:int):
		"""
			Constructor for TempAndHumClick4
		"""
		self.i2c = I2C(i2c_device, address)
		# set the address
		if address & self.ADDRESS_MASK_1:
			Pin(adr0, Pin.OUT, Pin.PULL_NONE).on()
		else:
			Pin(adr0, Pin.OUT, Pin.PULL_NONE).off()
		if address & self.ADDRESS_MASK_2:
			Pin(adr1, Pin.OUT, Pin.PULL_NONE).on()
		else:
			Pin(adr1, Pin.OUT, Pin.PULL_NONE).off()

	def get_raw(self):
		"""
			Private method for getting the raw data
		"""
		self.i2c.write(self.FETCH)
		time.sleep_ms(self.FETCH_DELAY_MS)
		buf = self.i2c.read(4)
		if len(buf) == 4:
			self.raw_temperature = int.from_bytes(result[:2], "big")
			self.raw_humidity = int.from_bytes(result[-2:], "big")
			self.status == self.STATUS_VALID_DATA
		else:
			self.status == self.STATUS_STALE_DATA

	def get_info(self) -> (int, int, int):
		"""
			Private method for getting the chip ID and config
		"""
		# TI device has no UUID
		manufacturer_id = self.i2c.write_read(self.MANUFACTURER_ID, 2)
		device_id = self.i2c.write_read(self.DEVICE_ID, 2)
		uuid = 0
		return (manufacturer_id, device_id, uuid)

	def set_resolution(self, temp_res: int, hum_res:int):
		"""
			Private method for setting the resolution
		"""
		config = self.HEATER_ENABLED
		if temp_res == 14:
			config |= self.TEMP_RES_14_BIT
		elif temp_res == 11:
			config |= self.TEMP_RES_11_BIT
		else:
			raise ValueError("Invalid temperature resolution")

		if hum_res == 14:
			config |= self.HUM_RES_14_BIT
		elif hum_res == 11:
			config |= self.HUM_RES_11_BIT
		elif hum_res == 8:
			config |= self.HUM_RES_8_BIT
		else:
			raise ValueError("Invalid humidity resolution")

		config_bytes = bytes([self.CONFIGURATION, config, 00])
		self.i2c.write(config_bytes)
