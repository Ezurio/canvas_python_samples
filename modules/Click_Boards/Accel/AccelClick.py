import time
from machine import Pin
from machine import I2C
import os

class AccelClick:
	"""
		Astract class for Accel Click board
	"""
	def set_mode(self, mode:int, data_rate:int):
		"""
			Abstract method for setting the mode
		"""
		pass

	def get_raw_values(self) -> any:
		"""
			Abstract method for getting raw values
		"""
		raise NotImplementedError("Subclass must implement abstract method")

	def get_signed_values(self) -> (int, int, int):
		"""
			Abstract method for getting signed values
		"""
		pass

	def get_difference(self) -> (int, int, int):
		"""
			Abstract method for getting the difference
		"""
		pass

	def to_signed(self, val:int) -> int:
		"""
			Private method for converting to signed as
			int.from_bytes() doesn't support signed values
		"""
		if val > 32767:
			val -= 65536
		return val

class Accel10Click(AccelClick):
	"""
		Accel10 Click board
	"""
	SET_DEV_ADDR = 0x18
	#
	LOW_POWER_MODE = 0x00
	HIGH_POWER_MODE = 0x04
	SINGLE_SHOT_MODE = 0x08
	#
	POWER_DOWN_DR = 0x00
	HIGH_POWER_DR_12_5HZ = 0x20
	HIGH_POWER_DR_25HZ = 0x30
	HIGH_POWER_DR_50HZ = 0x40
	HIGH_POWER_DR_100HZ = 0x50
	HIGH_POWER_DR_200HZ = 0x60
	HIGH_POWER_DR_400HZ = 0x70
	HIGH_POWER_DR_800HZ = 0x80
	HIGH_POWER_DR_1600HZ = 0x90
	#
	LOW_POWER_DR_1_6HZ = 0x10
	LOW_POWER_DR_12_5HZ = 0x20
	LOW_POWER_DR_25HZ = 0x30
	LOW_POWER_DR_50HZ = 0x40
	LOW_POWER_DR_100HZ = 0x50
	LOW_POWER_DR_200HZ = 0x60

	def __init__(self, i2c_device:any) -> None:
		"""
			Constructor for Accel10Click
		"""
		self.i2c = I2C(i2c_device, self.SET_DEV_ADDR)
		self.prev_x = 0
		self.prev_y = 0
		self.prev_z = 0

	def set_mode(self, mode:int, data_rate:int):
		"""
		"""
		self.i2c.write(b"\x20" + bytes([mode | data_rate]))

	def get_raw_values(self) -> any:
		"""
			Private method for getting raw values
		"""
		self.i2c.write(b"\x22\x03")
		return self.i2c.write_read(b"\x28",6)

	def get_signed_values(self) -> (int, int, int):
		self.i2c.write(b"\x22\x03")
		vals = self.i2c.write_read(b"\x28",6)
		x = int.from_bytes(vals[0:2], "little")
		x = self.to_signed(x)
		y = int.from_bytes(vals[2:4], "little")
		y = self.to_signed(y)
		z = int.from_bytes(vals[4:6], "little")
		z = self.to_signed(z)
		return (x, y, z)

	def get_difference(self) -> (int, int, int):
		"""
			Private method for getting the difference
		"""
		x, y, z = self.get_signed_values()
		dx = x - self.prev_x
		dy = y - self.prev_y
		dz = z - self.prev_z
		self.prev_x = x
		self.prev_y = y
		self.prev_z = z
		return (dx, dy, dz)
