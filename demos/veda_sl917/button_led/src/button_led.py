from machine import Pin
import os

class App:
    app_id = 'veda_sl917_explorer_board_button_led_demo'
    app_ver = '0.1.0'

    def __init__(self):
        self.led0 = Pin('LED0', Pin.OUT, Pin.PULL_NONE)
        self.led1 = Pin('LED1', Pin.OUT, Pin.PULL_NONE)
        self.btn0 = Pin('BUTTON0', Pin.IN, Pin.PULL_NONE)
        self.btn1 = Pin('BUTTON1', Pin.IN, Pin.PULL_UP)

    def button0_handler(self, v):
        # Toggle LED0 if button0 is pressed
        if self.btn0.value() == 0:
            self.led0.toggle()

    def button1_handler(self, v):
        # Toggle LED1 if button1 is pressed
        if self.btn1.value() == 0:
            self.led1.toggle()
    
    def start(self):
        # Setup button press/release handlers
        self.btn0.configure_event(self.button0_handler, Pin.EVENT_BOTH)
        self.btn1.configure_event(self.button1_handler, Pin.EVENT_BOTH)

# If this script is run directly, start the application
if __name__ == '__main__':
    print('ezurio CANVAS v' + os.uname().release + ' on ' + os.uname().machine)
    print('Veda SL917 - ' + App.app_id + ' v' + App.app_ver)
    app = App()
    app.start()
