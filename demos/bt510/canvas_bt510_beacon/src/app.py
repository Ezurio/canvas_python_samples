from board import Board
from bluetooth import Bluetooth
from temperature import TemperatureSensor
from accelerometer import Accelerometer
from open_close import OpenCloseSensor
from button import Button
from led import Led
from power import Power
from canvas import Timer
import time

class App:
    ble_advertising_name = 'BT510'
    board = None
    bluetooth = None
    temperature = None
    accelerometer = None
    open_close = None
    button = None
    led = None
    battery_ok = None
    battery_mv = 0
    timer = None
    counter = 0
    company_id = bytes([0x77, 0x00])
    canvas_bt510_protocolid = bytes([0xc9, 0x00])

    def __init__(self):
        self.board = Board()
        self.bluetooth = Bluetooth()
        self.temperature = TemperatureSensor()
        self.accelerometer = Accelerometer()
        self.open_close = OpenCloseSensor()
        self.button = Button()
        self.led = Led()

    def update_advertising_data(self, data):
        # Update the advertising data with the current battery status
        self.battery_ok = self.temperature.get_battery_ok()
        if ((self.counter+1) & 0x40) != 0 and  (self.counter & 0x40) == 0:
            self.update_battery_voltage()
        accel_bytes = self.accelerometer.accelerometer.write_read(b"\xa8", 6)
        flags = 0x06
        # If battery low, set the battery low flag bit 0x01
        if not self.battery_ok:
            flags |= 0x01
        # Read the mag sensor
        if self.open_close.is_open():
            flags &= ~0x02
        # Read the button
        if not self.button.is_pressed():
            flags &= ~0x04
        # take a temperature reading
        self.temperature.get_temperature_string()
        self.bluetooth.set_custom_data(self.company_id + self.canvas_bt510_protocolid + accel_bytes + bytes([self.counter & 0xFF]) + bytes([flags]) + self.temperature.temp_sample + self.battery_mv.to_bytes(2, 'big'))
        self.counter += 1

    def button_change_callback(self, data):
        if data:
            self.led.green_off()
        else:
            self.led.green_on()

    def magnet_change_callback(self, data):
        if data:
            self.led.red_off()
        else:
            self.led.red_on()

    def test_peripherals(self):
        # Test the temperature sensor
        self.temperature.enable()
        print('Temperature:', self.temperature.get_temperature_string(), 'C')

        # Test the accelerometer
        self.accelerometer.enable()
        print('Accelerometer:', self.accelerometer.get_acceleration_string())

        # Test the button by setting up an event handler
        # NOTE: Enabling the button for event detection adds ~20uA to the current draw.
        #       To save power, only enable the button when needed, 
        #       take a reading, then disable it.
        self.button.enable()
        self.button.on_change(self.button_change_callback)

        # Test the magnet sensor by setting up an event handler
        # NOTE: Enabling the magnet sensor for event detection adds ~20uA to the current draw.
        #       To save power, only enable the magnet sensor when needed, 
        #       take a reading, then disable it.
        self.open_close.enable()
        self.open_close.on_change(self.magnet_change_callback)
    
    def update_battery_voltage(self):
        # Read voltage with the green LED on to add some load on the battery
        self.led.green_on()
        time.sleep_ms(50)
        self.battery_mv = Power.get_battery_voltage_mv()
        self.led.green_off()
        # If battery_ok is False, the battery is low. Blink the red LED to indicate this.
        if not self.battery_ok:
            self.led.red_on()
            time.sleep_ms(100)
            self.led.red_off()

    def start(self):
        print('App is running')

        # Enable the temperature sensor to get the battery status.
        # When not being queried, the temperature sensor will 
        # return to deep sleep state on its own.
        self.temperature.enable()
        self.battery_ok = self.temperature.get_battery_ok()

        # Enable LED control
        self.led.enable()

        # Update the battery voltage reading
        self.update_battery_voltage()

        # Enable Bluetooth for advertising
        self.bluetooth.enable()
        # Set the device name in the BLE advertisement to BT5.
        # The name will be suffixed with 4 characters from the Bluetooth device address.
        self.bluetooth.set_name('BT5')
        # Set the transmit power to 0 dBm for decent power/range tradeoff
        self.bluetooth.set_tx_power(0)
        # Set the manufacturer specific data section to include the device id
        # and a byte containing 1 if the battery is OK, 0 if it is low
        #self.bluetooth.set_custom_data(self.company_id + bytes(self.bluetooth.get_device_id(), 'utf-8') + bytes([self.battery_ok]) + self.battery_mv.to_bytes(2, 'little'))
        self.temperature.enable()
        self.accelerometer.enable()
        self.open_close.enable()
        self.button.enable()
        self.update_advertising_data(None)
        
        # Start advertising a non-connectable "beacon" at an 
        # interval of 1 second (1000ms) to conserve battery
        connectable = True
        scannable = False
        extended = True
        advertising_interval_ms = 500
        self.bluetooth.start_advertising(connectable, scannable, extended, advertising_interval_ms)

        # Setup a timer to periodically update the advertising data
        # This will update the battery voltage and status in the advertising data
        self.timer = Timer(1000, True, self.update_advertising_data, None)
        self.timer.start()

        # Default to LEDs off
        self.led.green_off()
        self.led.red_off()

        # Test the peripherals
        # NOTE: Comment out the next line to save power. This function demonstrates interfacing with peripherals
        #self.test_peripherals()

        # Put the REPL interface to sleep to save power
        Power.repl_sleep(20000)
