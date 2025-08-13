"""
This ADC sample works on the MG100 and Pinnacle 100 DVK.
On the Pinnacle 100 DVK, the ADC is used to measure the voltage level that powers the board.
On the MG100, the battery voltage is measured. This only works for the MG100 with battery backup.
"""

import machine
import canvas
import os

is_mg100 = False
if "mg100" == os.uname().machine:
    is_mg100 = True
elif "pinnacle_100_dvk" != os.uname().machine:
    raise Exception("This sample only works on the MG100 and Pinnacle 100 DVK")

# The following constant values are based on the MG100 and Pinnacle 100 DVK hardware.
MEASURE_EN_PIN = 'VIN_ADC_EN'
ADC_CHANNEL = 5
ATTENUATION = 4
if is_mg100:
    MEASURE_EN_PIN = 'VBAT_EN'
    ADC_CHANNEL = 1
    # There is enough headroom to use a gain of 1 on the MG100.
    # This gives us the best resolution when reading the battery voltage.
    ATTENUATION = 1
GAIN = 1
SAMPLE_TIME_NS = 40000
RESOLUTION = 16
ADC_MAX_COUNTS = 2 ** RESOLUTION - 1
VREF = 1.8 / 4
# Voltage divider resistors
R1 = 13000
R2 = 1100

ADC_READ_INTERVAL_MS = 5000

en = machine.Pin(MEASURE_EN_PIN, machine.Pin.OUT)
adc = machine.ADC(ADC_CHANNEL)
adc.init(sample_ns=SAMPLE_TIME_NS, atten=ATTENUATION, gain=GAIN)


def enable_measure(enable: bool):
    if enable:
        en.high()
    else:
        en.low()


def read_adc():
    enable_measure(True)
    counts = adc.read_u16()
    enable_measure(False)
    print('Raw: ', counts)
    voltage = counts / ADC_MAX_COUNTS * VREF
    print('Raw voltage: ', voltage)
    voltage = voltage * ATTENUATION / GAIN
    print('Gain adjust: ', voltage)
    voltage = voltage * (R1 + R2) / R2
    print('Source voltage: ', voltage)
    return voltage


def read_cb(data):
    read_adc()


read_timer = canvas.Timer(ADC_READ_INTERVAL_MS, True, read_cb, None)
read_timer.start()
