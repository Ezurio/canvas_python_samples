from TempAndHumClick import TempAndHumClickBase

class TempAndHumClickFormat(TempAndHumClickBase):
	def get_temp_c(self) -> float:
		self.get_raw()
		temperature = (float)(self.raw_temperature)
		temperature *= self.MULTIPLIER_COEF_TEMP
		temperature /= (float)(self.DIVISOR_TEMP)
		temperature += self.ADDITION_COEF_TEMP
		return temperature

	def get_humidity(self) -> float:
		self.get_raw()
		humidity = (float)(self.raw_humidity)
		humidity *= self.MULTIPLIER_COEF_HUM
		humidity /= (float)(self.DIVISOR_HUM)
		return humidity

	def get_temp_f(self)->float:
		return ((self.get_temp_c() * 9.0) / 5.0) + 32.0


