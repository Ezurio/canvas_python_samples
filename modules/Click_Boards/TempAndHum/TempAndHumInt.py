from TempAndHumClick import TempAndHumClickBase

class TempAndHumClickFormat(TempAndHumClickBase):
	def get_temp_c(self) -> int:
		self.get_raw()
		temperature = self.raw_temperature
		temperature *= self.MULTIPLIER_COEF_TEMP
		temperature //= self.DIVISOR_TEMP
		temperature += self.ADDITION_COEF_TEMP
		return temperature

	def get_humidity(self) -> int:
		self.get_raw()
		humidity = self.raw_humidity
		humidity *= self.MULTIPLIER_COEF_HUM
		humidity //= self.DIVISOR_HUM
		return humidity

	def get_temp_f(self)->int:
		return ((self.get_temp_c() * 9) // 5) + 32
