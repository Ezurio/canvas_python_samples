from machine import Pin
import time
import os

un = os.uname()
print('\r\n\x1b[48;5;0m' + ' ' * 80 + '\x1b[0m')
print('\x1b[38;5;231;48;5;0m' + '{:^80}'.format('ezurio CANVAS v' + un.release + ' on ' + un.machine) + '\x1b[0m')
print('\x1b[48;5;0m' + ' ' * 80 + '\x1b[0m')
enter_config_mode = False
btn0 = Pin('BUTTON0', Pin.IN, Pin.PULL_NONE)
led0 = Pin('LED0', Pin.OUT, Pin.PULL_NONE)
if btn0.value() == 0:
    led0.on()
    enter_config_mode = True
    print('Button pressed, entering configuration mode')
else:
    print('Loading...')

time.sleep_ms(50)
