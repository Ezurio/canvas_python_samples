import time
from app import App

print('\x1b[1F\x1b[37;48;5;160m' + '{:^80}'.format('Veda SL917 - ' + App.app_id + ' v' + App.app_ver) + '\x1b[0m')
app = App()
# enter_config_mode set by boot.py
app.start(enter_config_mode)
