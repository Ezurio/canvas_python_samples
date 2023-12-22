import canvas
import canvas_ble
import machine
from machine import Pin
from machine import I2C
import time

app_id='tiltad'
app_ver='1.4.0'

config = { }
event_data = { }
event_data['ctr'] = 0
event_data['iic_accel_on'] = b"\xa0\x2f"
event_data['iic_accel_off'] = b"\xa0\x08"
event_data['hdr'] = b"\x77\x00\xc9\x00"

def load_config():
    global config

    # Set default configuration values
    config["reporting_interval_ms"] = 200
    config["ble_name"] = "BT510"
    
    # Load configuration from a file
    try:
        f = open("config.cb", "rb")
    except:
        print("Configuration file not found, saving defaults")
        save_config()
        return
    
    # Read the entire file
    cbor = f.read()
    f.close()
    if cbor is None:
        print("Configuration file is empty, saving defaults")
        save_config()
        return
    
    # Convert CBOR to an object
    config_file = canvas.zcbor_to_obj(cbor)
    if config_file is None:
        print("Configuration is corrupt, saving defaults")
        save_config()
        return
    
    # Copy the configuration from the file
    for c in config_file:
        config[c] = config_file[c]

def save_config():
    global config

    config_file = { }

    # Copy config values from the live config object
    config_file["reporting_interval_ms"] = config["reporting_interval_ms"]
    config_file["ble_name"] = config["ble_name"]

    # Convert the configuration to CBOR
    cbor = canvas.zcbor_from_obj(config_file, 0)
    if cbor is None:
        print("Unable to convert configuration to CBOR")
        return
    
    # Write the CBOR to a file
    f = open("config.cb", "wb")
    if f is None:
        print("Unable to open configuration file")
        return
    
    size = f.write(cbor)
    f.close()

def disconnect_pin(bank, idx):
    bank_str = "gpio@50000000"
    if bank > 0:
        bank_str = "gpio@50000300"
    pin = Pin((bank_str, idx), Pin.NO_CONNECT, Pin.PULL_NONE)

def ble_connect(conn):
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))

def ble_disconnect(conn):
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    event_data['adv'].start()

def timer_callback(event):
    # Enable accelerometer
    event['accel_iic'].write(event['iic_accel_on'])
    time.sleep_ms(1)
    accel_sample = event['accel_iic'].write_read(b"\xa8",6)
    event['accel_iic'].write(event['iic_accel_off'])
    temp_sample = event['temp_iic'].write_read(b"\xe3", 2)
    temp_status = event['temp_iic'].write_read(b"\xe7", 1)
    flags = 0x06
    # If battery low, set the battery low flag bit 0x01
    if temp_status[0] & 0x40:
        flags |= 0x01
    # Read the mag sensor
    if event['mag_sensor'].value():
        flags &= ~0x02
    # Read the button
    if event['button'].value():
        flags &= ~0x04
    # Update BLE Advertisement
    event['adv'].clear_buffer(False)
    event['adv'].add_ltv(0x01, bytes([0x06]), False)
    event['adv'].add_tag_string(0x09, event['ble_name'], False)
    event['adv'].add_ltv(0xff, event_data['hdr'] + accel_sample + bytes([event['ctr'], flags]) + temp_sample, False)
    event['adv'].update()
    event['ctr'] = event['ctr'] + 1

def init_application():
    global config
    # Load configuration
    load_config()
    # Init I2C
    event_data['accel_iic'] = I2C("i2c@40003000", 0x18)
    # Init the temperature sensor
    event_data['temp_iic'] = I2C("i2c@40003000", 0x40)    
    # Init the button
    event_data['button'] = Pin(("gpio@50000300", 10), Pin.IN, Pin.PULL_UP)
    # Init the mag sensor
    event_data['mag_sensor'] = Pin(("gpio@50000300", 14), Pin.IN, Pin.PULL_NONE)
    # Init BLE
    canvas_ble.init()
    canvas_ble.set_periph_callbacks(ble_connect, ble_disconnect)
    devid = canvas_ble.addr_to_str(canvas_ble.my_addr())[10:12] + canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14]
    event_data['ble_name'] = config['ble_name'] + "-" + devid
    event_data['adv'] = canvas_ble.Advertiser()
    event_data['adv'].set_properties(True, False, True)
    event_data['adv'].set_interval(config["reporting_interval_ms"], config["reporting_interval_ms"] + 10)
    event_data['adv'].clear_buffer(False)
    event_data['adv'].add_ltv(0x01, bytes([0x06]), False)
    event_data['adv'].add_tag_string(0x09, event_data['ble_name'], False)
    event_data['adv'].add_ltv(0xff, event_data['hdr'] + b"\xb00\xb00\xb00\xb00\xb00\xb00\x00", False)
    # Start BLE Advertising
    event_data['adv'].start()
    # Print help text
    print(' \r\n\r\nBT510 tilt sensor script ' + app_ver)
    print('------------------------------')
    print("          BLE Name: " + event_data['ble_name'])
    print('Reporting Interval: ' + str(config["reporting_interval_ms"]) + 'ms')
    print('Press ctrl-c within 15 seconds to access the REPL and cancel low power mode\r\n')
    time.sleep_ms(15000)
    print('Entering low power mode, UART REPL will turn off in 20 seconds...\r\n')
    # Start countdown to disable REPL UART
    machine.console_sleep()
    # ID pins
    disconnect_pin(1, 1)
    disconnect_pin(0, 2)
    disconnect_pin(0, 25)
    # LED pins
    disconnect_pin(0, 22)
    disconnect_pin(0, 25)
    # TM Pin
    disconnect_pin(0, 3)
    # BATT_V and BATT_READ pins
    disconnect_pin(0, 28)
    disconnect_pin(1, 15)
    # Interrupt pins
    disconnect_pin(1, 5)
    disconnect_pin(1, 12)
    # Setup accelerometer
    event_data['accel_iic'].write(b"\x1e\x90")
    time.sleep_ms(1000)

init_application()
timer = canvas.Timer(config["reporting_interval_ms"], True, timer_callback, event_data)
timer.start()
