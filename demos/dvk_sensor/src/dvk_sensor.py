#
# Ezurio DVK Sensor Demo
#
# This application provides a simple framework for reading sensors
# attached to an Ezurio DVK board and advertising the data over
# Bluetooth LE. Sensors are typically connected via mikroBUS or
# QWIIC interface. Use the Xbit desktop or mobile application to
# scan for and view advertised data using the "DVK Sensor Monitor" Applet.
#
# Supported DVK boards:
# - BL54L15/BL54L15u DVK
# - Veda SL917 SoC Explorer Board (brd2911a)
# - Lyra 24 Series Development Kits
#
# Supported Sensors:
# - TempHum4 Click (I2C Temperature and Humidity sensor)
# - LTR-329 Light Sensor (I2C Ambient Light sensor)
#
# Advertising Data Format:
# 7700 company id
# ca00 dvk sensor protocol id
# xx 8 bit running counter
# da06 power_mv
# 05 button_flags
# 00 led_flags
# The bytes to follow are zero or more sensor-specific data fields:
# 10 2040c741 c0b51842 [Sensor 0x10 data (TempHum4Click)]
# 11 a040 0040 [Sensor 0x11 data (LTR-329)]
#

from micropython import const
import time
import os
from machine import I2C, Pin
import struct
from canvas import Timer
import canvas_ble
import struct

fmt_cyan = const("\x1b[1;38;5;87m")
fmt_green = const("\x1b[38;5;231;48;5;28m")
fmt_stop = const("\x1b[0m")
fmt_red = const("\x1b[1;38;5;231;48;5;88m")
fmt_white = const("\x1b[1;38;5;231m")
fmt_amber = const("\x1b[1;38;5;214m")
fmt_dark = const("\x1b[38;5;236;48;5;235m")

class BoardInfo:
    un = os.uname()
    BL54L15_DVK = const('bl54l15_dvk')
    BRD2911A = const('brd2911a')
    LYRA24_SERIES = const('lyra24') # prefix for all supported Lyra24 boards

    @staticmethod
    def isBoard(board_name):
        if BoardInfo.un.machine == board_name:
            return True
        # For Lyra24 series, check for prefix match
        if board_name == BoardInfo.LYRA24_SERIES:
            return BoardInfo.un.machine.startswith(BoardInfo.LYRA24_SERIES)
        return False

if BoardInfo.isBoard(BoardInfo.BL54L15_DVK):
    from machine import ADC

class Buttons:
    def __init__(self):
        if BoardInfo.isBoard(BoardInfo.BL54L15_DVK):
            self.buttons = [Pin('BUTTON0', Pin.IN, Pin.PULL_UP),
                            Pin('BUTTON1', Pin.IN, Pin.PULL_UP),
                            Pin('BUTTON2', Pin.IN, Pin.PULL_UP),
                            Pin('BUTTON3', Pin.IN, Pin.PULL_UP)]
        elif BoardInfo.isBoard(BoardInfo.BRD2911A):
            self.buttons = [Pin('BUTTON0', Pin.IN, Pin.PULL_NONE),
                            Pin('BUTTON1', Pin.IN, Pin.PULL_UP)]
        elif BoardInfo.isBoard(BoardInfo.LYRA24_SERIES):
            self.buttons = [Pin('BTN0', Pin.IN, Pin.PULL_UP)]
        else:
            self.buttons = []
        self.buttons_pressed = [False] * len(self.buttons)

    def read(self):
        # Buttons are active low
        self.buttons_pressed = [False if b.value() == 1 else True for b in self.buttons]

    def get_flags(self):
        flags = 0x00
        for i, pressed in enumerate(self.buttons_pressed):
            if pressed:
                flags |= (1 << i)
        return flags

    def on_button_change(self, callback, button_index):
        if len(self.buttons) > button_index and self.buttons[button_index] is not None:
            self.buttons[button_index].configure_event(callback, Pin.EVENT_BOTH)


class Leds:
    def __init__(self):
        if BoardInfo.isBoard(BoardInfo.BL54L15_DVK):
            self.leds = [Pin('LED0', Pin.OUT, Pin.PULL_NONE),
                         Pin('LED1', Pin.OUT, Pin.PULL_NONE),
                         Pin('LED2', Pin.OUT, Pin.PULL_NONE),
                         Pin('LED3', Pin.OUT, Pin.PULL_NONE)]
        elif BoardInfo.isBoard(BoardInfo.BRD2911A):
            self.leds = [None, # special case, disable LED0, conflict with MikroBUS INT pin
                         Pin('LED1', Pin.OUT, Pin.PULL_NONE)]
        elif BoardInfo.isBoard(BoardInfo.LYRA24_SERIES):
            self.leds = [Pin('LED', Pin.OUT, Pin.PULL_NONE)]
        self.led_states = [0] * len(self.leds)  # Store states of the LEDs

    def set(self, led_index, state):
        # LEDs are active high
        if len(self.leds) > led_index and self.leds[led_index] is not None:
            self.led_states[led_index] = state
            self.leds[led_index].value(state)
    
    def toggle(self, led_index):
        new_state = 1 - self.led_states[led_index]
        self.set(led_index, new_state)

    def set_all(self, state):
        for i in range(len(self.leds)):
            self.led_states[i] = state
            self.set(i, state)

    def get_flags(self):
        flags = 0x00
        for i, state in enumerate(self.led_states):
            if state:
                flags |= (1 << i)
        return flags

class Bluetooth:
    ble_name = 'Canvas'
    advertiser = None
    ble_enabled = False
    is_advertising = False
    device_id = None
    is_connectable = False
    is_scannable = False
    is_extended = True
    advertising_interval_ms = 1000
    ble_custom_data = b"\xb00\xb00"
    debug = False

    def __init__(self):
        pass

    def _ble_connected(self, conn):
        pass

    def _ble_disconnected(self, conn):
        if self.is_advertising: 
            self.advertiser.start()

    def set_name(self, new_name):
        self.ble_name = new_name
        if self.ble_enabled and self.is_advertising:
            self.update_advertisement()

    def set_custom_data(self, new_data):
        self.ble_custom_data = new_data
        if(self.debug):
            print(new_data)
        if self.ble_enabled and self.is_advertising:
            self.update_advertisement()
    
    def get_device_id(self):
        return self.device_id
    
    def set_tx_power(self, dbm):
        if self.ble_enabled:
            canvas_ble.set_tx_power(dbm*10)

    def enable(self):
        if self.ble_enabled:
            return
        canvas_ble.init()
        canvas_ble.set_periph_callbacks(self._ble_connected, self._ble_disconnected)
        self.device_id = canvas_ble.addr_to_str(canvas_ble.my_addr())[10:12] + canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14]
        self.advertiser = canvas_ble.Advertiser()
        self.advertiser.stop()
        self.ble_enabled = True

    def start_advertising(self, connectable=False, scannable=False, extended=True, advertising_interval_ms=1000, primary_phy=canvas_ble.PHY_1M, secondary_phy=canvas_ble.PHY_2M):
        if self.ble_enabled and not self.is_advertising:
            self.is_connectable = connectable
            self.is_scannable = scannable
            self.is_extended = extended
            self.advertiser.set_properties(self.is_connectable, self.is_scannable, self.is_extended)
            self.advertiser.set_phys(primary_phy, secondary_phy)
            self.advertising_interval_ms = advertising_interval_ms
            self.advertiser.set_interval(advertising_interval_ms, advertising_interval_ms + 10)
            self.update_advertisement()
            self.advertiser.start()
            self.is_advertising = True

    # Stop advertising
    def stop_advertising(self):
        if self.ble_enabled and self.is_advertising:
            self.advertiser.stop()
            self.is_advertising = False

    # Stop advertising
    def disable(self):
        if self.ble_enabled:
            if self.is_advertising:
                self.stop_advertising()
            # intentionally not setting ble_enabled = False here to avoid multiple calls to canvas_ble.init()

    # Update BLE Advertisement
    def update_advertisement(self):
        if self.ble_enabled:
            self.advertiser.clear_buffer(False)
            self.advertiser.clear_buffer(True)            
            self.advertiser.add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([0x06]), False)
            self.advertiser.add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, self.ble_name + '-' + self.device_id, False)
            self.advertiser.add_ltv(canvas_ble.AD_TYPE_MANU_SPECIFIC, self.ble_custom_data, False)
            if self.is_advertising:
                self.advertiser.update()

class Sensor:
    @staticmethod
    def i2c_address():
        raise NotImplementedError("i2c_address method must be implemented by subclasses")

    def is_present(self):
        raise NotImplementedError("is_present method must be implemented by subclasses")

    def configure(self):
        raise NotImplementedError("configure method must be implemented by subclasses")

    def read(self):
        raise NotImplementedError("read_data method must be implemented by subclasses")
    
    def disable(self):
        raise NotImplementedError("disable method must be implemented by subclasses")
    
    def get_advertising_bytes(self):
        raise NotImplementedError("get_advertising_bytes method must be implemented by subclasses")

class TempHum4ClickSensor(Sensor):
    BLE_SENSOR_TAG_ID = 0x10

    I2C_ADDRESSES = [0x40, 0x41, 0x42, 0x43]
    MAX_CONVERSION_TIME_MS = 40

    def __init__(self, i2c):
        self.i2c = i2c
        # Cycle through alternate addresses to find the sensor
        self.address = None
        for addr in self.I2C_ADDRESSES:
            self.i2c.set_address(addr)
            if self.is_present():
                self.address = addr
                break

        if self.address is not None:
            self.configure()
            print(fmt_green + '{:^80}'.format('TempHum4 Click detected ('+str(hex(self.address))+')') + fmt_stop)
        else:
            print(fmt_red + '{:^80}'.format('WARNING: TempHum4 Click not detected.') + fmt_stop)
    
    @staticmethod
    def i2c_address():
        return TempHum4ClickSensor.I2C_ADDRESSES[0]

    def is_present(self):
        mfr = self.i2c.write_read(b"\xFE", 2)
        if mfr != b'TI':
            return False
        deviceid = self.i2c.write_read(b"\xFF", 2)
        if deviceid != b'\x10\x00':
            return False
        return True

    def configure(self):
        # Configure for 14-bit temperature and humidity
        self.i2c.write(b"\x02\x10\x00")

    def read(self):
        # Start conversion, wait, and read result
        self.i2c.write(b"\x00")
        time.sleep_ms(self.MAX_CONVERSION_TIME_MS)
        # If the results aren't ready, then 4 bytes won't be returned.
        result = self.i2c.read(4)
        #print('TempHum4 raw data:', result)
        self.data = {}
        if result is not None and len(result) == 4:
            temp_raw = int.from_bytes(result[:2], "big")
            self.data['temperature'] = ((temp_raw / 65536.0) * 165.0) - 40.0
            hum_raw = int.from_bytes(result[-2:], "big")
            self.data['humidity'] = (hum_raw / 65536.0) * 100.0
        else:
            self.data = None
        return self.data
    
    def disable(self):
        # Put the sensor into low power mode
        # not implemented
        pass

    def get_advertising_bytes(self):
        if self.data is None:
            return bytes()
        return struct.pack('<Bff', self.BLE_SENSOR_TAG_ID, self.data['temperature'], self.data['humidity'])        

class LTR329Sensor(Sensor):
    BLE_SENSOR_TAG_ID = 0x11

    LTR329ALS_ADDR        = const(0x29)

    REG_ALS_CONTR         = const(0x80) # Operation mode control
    REG_ALS_MEAS_RATE     = const(0x85) # Measurement Rate Register
    REG_ALS_PART_ID       = const(0x86) # Part ID Register
    REG_ALS_MANUF_ID      = const(0x87) # Manufacturer ID Register
    REG_ALS_DATA_CH1_0    = const(0x88) # ALS Data Channel 1 low byte
    REG_ALS_DATA_CH1_1    = const(0x89) # ALS Data Channel 1 high byte
    REG_ALS_DATA_CH0_0    = const(0x8A) # ALS Data Channel 0 low byte
    REG_ALS_DATA_CH0_1    = const(0x8B) # ALS Data Channel 0 high byte
    REG_ALS_STATUS        = const(0x8C) # ALS Status Register

    ALS_CONTR_RESET          = const(0x02) # Software Reset Command
    ALS_CONTR_MODE_ACTIVE    = const(0x01) # Activate the Sensor
    ALS_MANUFAC_ID           = const(0x05) # Manufacturer ID
    ALS_PART_ID              = const(0xA0) # Part number = 10, Rev = 0
    ALS_INIT_STARTUP_TIME_MS = const(100)  # Initial startup time in ms
    ALS_WAKEUP_TIME_MS       = const(10)   # Delay after software reset in ms

    no_data = {}

    def __init__(self, i2c):
        self.i2c = i2c
        self.configure()
        if self.is_present():
            print(fmt_green + '{:^80}'.format('LTR-329 Light Sensor detected') + fmt_stop)
        else:
            print(fmt_red + '{:^80}'.format('WARNING: LTR-329 Light Sensor not detected.') + fmt_stop)
        self.data = self.no_data

    @staticmethod
    def i2c_address():
        return LTR329ALS_ADDR  # I2C address for LTR-329

    # Attempt to read a register to check if the device is present
    def is_present(self):
        try:
            # Read the Manufacturer ID
            self.mfg_id = self.i2c.write_read(bytes([REG_ALS_MANUF_ID]), 1)
            #print("     ALS Mfg ID:", self.mfg_id.hex())

            # Read the Part ID
            self.part_id = self.i2c.write_read(bytes([REG_ALS_PART_ID]), 1)
            #print("ALS Part Number:", hex(self.part_id[0] >> 4))
            #print("   ALS Part Rev:", hex(self.part_id[0]&0x0F))
            if self.mfg_id[0] == 0x05 and (self.part_id[0] >> 4) == 0x0A:
                return True
            return False
        except Exception:
            return False

    # Configuration code for LTR-329 sensor
    def configure(self):
        # Allow time for the sensor to power up
        time.sleep_ms(ALS_INIT_STARTUP_TIME_MS)

        # Send a software reset command
        self.i2c.write(bytes([REG_ALS_CONTR, ALS_CONTR_RESET]))

        # Configure the ALS control register to activate the sensor
        self.i2c.write(bytes([REG_ALS_CONTR, ALS_CONTR_MODE_ACTIVE]))

        # Wait for the sensor to wake up from standby
        time.sleep_ms(ALS_WAKEUP_TIME_MS)

        # Set the measurement rate to 200ms, integration time to 200ms
        # See ALS_MEAS_RATE register in LTR-329ALS datasheet for details
        self.i2c.write(bytes([REG_ALS_MEAS_RATE, 0x12]))
        pass

    # Read light level from the sensor
    def read(self):
        # Read ALS data from both channels
        ch1_low = self.i2c.write_read(bytes([REG_ALS_DATA_CH1_0]), 1)
        ch1_high = self.i2c.write_read(bytes([REG_ALS_DATA_CH1_1]), 1)
        ch0_low = self.i2c.write_read(bytes([REG_ALS_DATA_CH0_0]), 1)
        ch0_high = self.i2c.write_read(bytes([REG_ALS_DATA_CH0_1]), 1)

        try:
            # Combine high and low bytes for each channel
            self.data['visible'] = (ch0_high[0] << 8) | ch0_low[0]
            self.data['ir'] = (ch1_high[0] << 8) | ch1_low[0]
        except Exception:
            self.data = self.no_data
        return self.data

    def disable(self):
        # Disable the sensor
        self.i2c.write(bytes([REG_ALS_CONTR, 0x00]))  # Disable the Sensor
        pass

    def get_advertising_bytes(self):
        if self.data is None:
            return bytes()
        return struct.pack('<BHH', self.BLE_SENSOR_TAG_ID, self.data['visible'], self.data['ir'])

class App:
    app_id = "dvk_sensor_ble"
    app_ver = "0.1.0"
    counter = 0
    company_id = 0x0077
    canvas_dvk_sensor_protocolid = 0x00CA
    
    def __init__(self):
        if BoardInfo.isBoard(BoardInfo.BL54L15_DVK):
            self.power_adc = ADC(9)  # ADC9 is connected to VDD
        else:
            self.power_adc = None
            self.power_mv = 0
        self.bluetooth = Bluetooth()
        self.buttons = Buttons()
        self.leds = Leds()
        self.leds.set_all(0)  # Turn off all LEDs initially
        self.button_flags = 0x00  # No buttons pressed
        self.led_flags = 0x00  # No LEDs on

        # Set up button change callbacks using lambda
        for i in range(len(self.buttons.buttons)):
            self.buttons.on_button_change(lambda data, idx=i: self._on_button_change(idx, data), i)
        self._init_sensors()

    def _on_button_change(self, button_index, data):
        if data and button_index < len(self.leds.leds) and self.leds.leds[button_index] is not None:
            self.leds.toggle(button_index)

    def _init_sensors(self):
        i2c_bus = None
        self.sensors = []

        # Set I2C bus based on board type
        if BoardInfo.isBoard(BoardInfo.BL54L15_DVK):
            i2c_bus = "i2c@c8000"
        elif BoardInfo.isBoard(BoardInfo.BRD2911A):
            i2c_bus = ("I2C0","SDA","SCL")
        elif BoardInfo.isBoard(BoardInfo.LYRA24_SERIES):
            i2c_bus = ("I2C0","MB_SDA","MB_SCL")
        else:
            # Unsupported board
            return

        # Initialize I2C for TempHum4 Click sensor
        # NOTE: Address may vary on BL54L15 DVK since address lines are tied to buttons.
        # The code will cycle through possible addresses to find the sensor.
        self.th4click = TempHum4ClickSensor(I2C(i2c_bus, TempHum4ClickSensor.i2c_address()))
        if self.th4click.is_present():
            self.sensors.append(self.th4click)

        # Initialize I2C for LTR-329 sensor
        self.ltr329 = LTR329Sensor(I2C(i2c_bus, LTR329Sensor.i2c_address()))
        if self.ltr329.is_present():
            self.sensors.append(self.ltr329)

    def _read_sensors(self):
        if( self.power_adc is not None):
            self.power_mv = self.power_adc.read_uv() // 1000  # Convert microvolts to millivolts
        for sensor in self.sensors:
            sensor.read()

    def _update_advertising_data(self, data):
        self._read_sensors()
        sensor_data_bytes = bytes()

        for sensor in self.sensors:
            if sensor.is_present():
                sensor_bytes = sensor.get_advertising_bytes()
                if sensor_bytes is not None:
                    sensor_data_bytes += sensor_bytes

        self.buttons.read()
        self.button_flags = self.buttons.get_flags()
        self.led_flags = self.leds.get_flags()
        # Construct the advertising payload
        self.bluetooth.set_custom_data(struct.pack('<HHBhBB', self.company_id, self.canvas_dvk_sensor_protocolid, self.counter & 0xFF, self.power_mv, self.button_flags, self.led_flags) + sensor_data_bytes)
        self.counter += 1

    def start(self):
        self._read_sensors()
        self.bluetooth.enable()
        self.bluetooth.set_name('DVK-Sens')

        connectable = True
        scannable = False
        extended = True
        advertising_interval_ms = 250
        primary_phy = canvas_ble.PHY_1M
        secondary_phy = canvas_ble.PHY_2M
        self.bluetooth.start_advertising(connectable, scannable, extended, advertising_interval_ms, primary_phy, secondary_phy)

        self.timer = Timer(100, True, self._update_advertising_data, None)
        self.timer.start()

print('\r\n\x1b[48;5;0m' + ' ' * 80 + '\x1b[0m')
print('\x1b[38;5;231;48;5;0m' + '{:^80}'.format('ezurio CANVAS v' + BoardInfo.un.release + ' on ' + BoardInfo.un.machine) + '\x1b[0m')
print('\x1b[48;5;0m' + ' ' * 80 + '\x1b[0m')
time.sleep_ms(50)
print('\x1b[1F\x1b[37;48;5;160m' + '{:^80}'.format(BoardInfo.un.machine + ' - ' + App.app_id + ' v' + App.app_ver) + '\x1b[0m')
app = App()
app.start()
