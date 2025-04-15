# Read the BT510 battery voltage in millivolts
import machine

battery_adc = None
# Instantiate the battery voltage ADC
battery_adc = machine.ADC(9)
battery_adc.init(atten=6, reference=machine.ADC.REF_INTERNAL)
# Read the battery voltage in millivolts
battery_millivolts = battery_adc.read_uv() // 1000
print('\r\n\r\nBattery voltage: ' + str(battery_millivolts) + ' mV\r\n')

