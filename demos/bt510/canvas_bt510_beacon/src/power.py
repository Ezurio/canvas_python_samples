import machine

class Power:
    battery_adc = None

    def __init__(self):
        pass

    # Disable the REPL console UART for power saving
    @staticmethod
    def repl_sleep(timeout_ms):
        print('\r\nPutting REPL console to sleep in ' + str(timeout_ms//1000) + ' seconds')
        print('To cancel sleep and keep the REPL console active, type:')
        print('import machine')
        print('machine.console_wake()\r\n')
        machine.console_sleep(timeout_ms)
    
    # Enable the REPL console UART
    @staticmethod
    def repl_wake():
        machine.console_wake()
        print('Waking console UART')

    # Read the battery voltage in millivolts
    @staticmethod
    def get_battery_voltage_mv():
        # Instantiate the battery voltage ADC object if not already done
        if Power.battery_adc is None:
            Power.battery_adc = machine.ADC(9)
            Power.battery_adc.init(atten=6, reference=machine.ADC.REF_INTERNAL)
        return Power.battery_adc.read_uv() // 1000
