# This sample runs on the BL654 DVK and reads the temperature sensor (U1).
# A jumper must be placed on J6 to connect the temperature sensor to the ADC pin on the module.

import machine
import canvas

AIN1 = 2 # ADC channel 2. On zephyr platforms the ADC channels start at 1.
ADC_SAMPLE_TIME = 50000
ADC_ATTENUATION = 4
ADC_GAIN = 1
READ_SENSOR_INTERVAL_MS = 10000

adc = machine.ADC(AIN1)
adc.init(ADC_SAMPLE_TIME, ADC_ATTENUATION, ADC_GAIN)

def read_cb(data):
    # Vo(mV) = -11.67mV/ºC x T + 1858.3
    temp = adc.read_uv()
    print('Temperature (C): ', ((temp / 1000.0) - 1858.3) / -11.67)

read_timer = canvas.Timer(READ_SENSOR_INTERVAL_MS, True, read_cb, None)
read_timer.start()
