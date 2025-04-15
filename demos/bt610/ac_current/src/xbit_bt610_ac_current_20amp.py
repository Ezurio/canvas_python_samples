app_id='xbit_bt610_ac_current'
app_ver='2.0.0'

import canvas
import canvas_ble
from machine import ADC
from machine import I2C
from machine import Pin
import time

io_expander = None
io_expander_reset = None
io_expander_address = 0x70
analog_enable = None
therm_enable = None
adc = None
led1 = None
led2 = None
AIN1 = 1
AIN2 = 2
AIN3 = 3
AIN4 = 4
config = { }
event_data = { }
event_data['ctr'] = 0
event_data['hdr'] = b"\x77\x00\xcc\x00"
ac_current_test_counter = 0
console_display_enabled = False

def load_config():
    global config

    # Set default configuration values
    config["reporting_interval_ms"] = 1000
    config["ble_name"] = "BT610"
    config["network_id"] = 0xffff
    config["ain1_enabled"] = 1
    config["ain2_enabled"] = 0
    config["ain3_enabled"] = 0
    config["ain4_enabled"] = 0
    
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
    config_file["network_id"] = config["network_id"]
    config_file["ain1_enabled"] = config["ain1_enabled"]
    config_file["ain2_enabled"] = config["ain2_enabled"]
    config_file["ain3_enabled"] = config["ain3_enabled"]
    config_file["ain4_enabled"] = config["ain4_enabled"]

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

def ble_connect(conn):
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))

def ble_disconnect(conn):
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    event_data['adv'].start()

def get_test_ac_current_value():
    global ac_current_test_counter
    ac_current_test_counter = ac_current_test_counter + 100
    if(ac_current_test_counter > 20000):
        ac_current_test_counter = 0
    return ac_current_test_counter

def timer_callback(event):
    flags = 0x06

    if console_display_enabled:
        print("\r\033[36A")

    # Read the ac current sensor
    ac_current_sample = read_ac_current(AIN1) & 0xFFFF
    ac_bytes = ac_current_sample.to_bytes(2, 'big')
    #ac_bytes = get_test_ac_current_value().to_bytes(2, 'big') # Use a test value for AC current
    
    ac_current_sample = read_ac_current(AIN2) & 0xFFFF
    ac_bytes += ac_current_sample.to_bytes(2, 'big')
    #ac_bytes += get_test_ac_current_value().to_bytes(2, 'big') # Use a test value for AC current
    
    ac_current_sample = read_ac_current(AIN3) & 0xFFFF
    ac_bytes += ac_current_sample.to_bytes(2, 'big')
    #ac_bytes += get_test_ac_current_value().to_bytes(2, 'big') # Use a test value for AC current
    
    ac_current_sample = read_ac_current(AIN4) & 0xFFFF
    ac_bytes += ac_current_sample.to_bytes(2, 'big')
    #ac_bytes += get_test_ac_current_value().to_bytes(2, 'big') # Use a test value for AC current
    
    # Read the mag sensor
    if event['mag_sensor'].value():
        flags &= ~0x02
    # Read the button
    if event['button'].value():
        flags &= ~0x04
    # Upper 4 bits indicate ADC channels that are enabled (via local config)
    if(config.get("ain1_enabled") == 1):
        flags |= 0x10
    if(config.get("ain2_enabled") == 1):
        flags |= 0x20
    if(config.get("ain3_enabled") == 1):
        flags |= 0x40
    if(config.get("ain4_enabled") == 1):
        flags |= 0x80
    # Update BLE Advertisement
    event['adv'].clear_buffer(False)
    event['adv'].add_ltv(0x01, bytes([0x06]), False)
    event['adv'].add_tag_string(0x09, event['ble_name'], False)
    event['adv'].add_ltv(0xff, event_data['hdr'] + ac_bytes + bytes([event['ctr'] & 0xFF, flags]), False)
    event['adv'].update()
    event['ctr'] = event['ctr'] + 1

def init_leds():
    # Pin identified by gpio-dynamic label (device tree)
    led1 = Pin("LED1", Pin.OUT, 0)
    led1.off()

    # Pin identified by gpio-dynamic label (device tree)
    led2 = Pin("LED2", Pin.OUT, 0)
    led2.off()

def init_io_expander():
    global io_expander
    global io_expander_reset
    global io_expander_address

    io_expander = I2C("i2c@40003000", io_expander_address)
    io_expander_reset = Pin(("gpio@50000000", 28), Pin.OUT, Pin.PULL_NONE)

    # Reset the IO expander
    io_expander_reset.low()
    time.sleep_ms(1)
    io_expander_reset.high()
    time.sleep_ms(1)

def init_analog_enable():
    global analog_enable
    analog_enable = Pin(("gpio@50000300", 13), Pin.OUT, Pin.PULL_NONE)
    analog_enable.low() # disables analog circuit power

def init_therm_enable():
    global therm_enable
    therm_enable = Pin(("gpio@50000000", 10), Pin.OUT, Pin.PULL_NONE)
    therm_enable.low() # disables thermistor circuit power

def setup_for_current_sense():
    global adc

    # Setup ADC object to sample channel SIO_02/AIN0 of SoC (Labeled ADC_IN1 on BT610)
    adc = ADC(AIN1)
    
    # setup sample for 40000us (25Hz), attenuation of 4 (1/4), scale of 1 (no gain)
    adc.init(sample_ns=40000, atten=4, gain=1)

    # Setup port expander AIN address and port select pins as outputs
    # Register 3, 0b1 configures high impedance input, 0b0 configures as output
    # 0b11xxxxxx sets AUX1,AUX2 as inputs
    # 0bxxxx0000 sets AIN1,AIN2,AIN3,AIN4,AIN_A0,AIN_A1 as outputs
    io_expander.write(bytes([3,0b11000000]))

def read_current_sense(channel, ac_current_sensor_rating_amps, samples_to_average=10):
    global analog_enable
    global io_expander
    global adc

    # Enable the Analog Circuit power (VA)
    analog_enable.high()

    # Enable VREF for thermistor
    #therm_enable.high()

    time.sleep_us(200) # wait 200uS for analog switch startup/settling

    # Select the AINx input path by setting AIN_A0/AIN_A1 via io expander
    # Register 1, 0b0 output low, 0b1 output high. AIN1,AIN0 in bits 0b00xx0000
    #io_expander.write(bytes([1, (1 << (channel - 1)) | ((channel - 1) << 4)])) # thermistor setup
    io_expander.write(bytes([1, ((channel - 1) << 4)])) # current sense setup

    # Wait another 100us before starting to take samples
    time.sleep_us(100) # wait 100uS for analog switch startup/settling

    # Wait 100ms before sampling the ADC
    time.sleep_ms(100)

    # Perform samples_to_average ADC reads and average the result
    adc_value = 0
    adc_accum = 0
    for i in range(samples_to_average):
        adc_value = adc.read_u16()
        # interpret adc_value as a 2's complement number
        if adc_value & 0x8000:
            adc_value = -((~adc_value & 0xFFFF) + 1)
        adc_accum += adc_value
        #print(i, adc_value, adc_accum)
    adc_value = adc_accum // samples_to_average
    
    # Don't allow negative values
    if(adc_value < 0):
        adc_value = 0

    analog_enable.low()

    # Disable VREF for thermistor
    #therm_enable.low()

    # The voltage reference is set to 1/4 in software at the nRF52840 (VBAT / 4)
    # The BT610 has a 1/4 voltage divider in hardware on analog inputs
    # If VBAT is 3.55, the resulting voltage reference is 0.8875V, setting ADC counts at full scale
    # The ADC value is 14 bits shifted left 2 bits so full scale is 0-65535
    # The divisor is calculated by dividing 65535 by 0.8875 to get 73842
    # The ADC value is then multiplied by 1000 to provide a 3 decimal place result with integer math
    # The voltage is then calculated by dividing the ADC value by 73842 and multiplying by 16
    
    # NOTE: the value used here has been tweaked slightly based on empirical testing.
    #       Adjust according to your setup for more accurate results.
    voltage_times_1000 = ((adc_value*1000) // 75840) * 16

    # The current sensor is rated for 20A and outputs 5V at full scale
    amps_rms_times_1000 = ((voltage_times_1000 // 5) * ac_current_sensor_rating_amps)

    return [adc_value, voltage_times_1000, amps_rms_times_1000]

def init_application():
    global config
    global event_data

    # Initialize the LEDs
    init_leds()

    # Load configuration
    load_config()

    # Initialize the IO expander, analog enable pin, and ADC peripheral
    init_io_expander()
    init_analog_enable()
    init_therm_enable()

    # Initialize the analog chain for current sensing on AIN1-AIN4
    setup_for_current_sense()

    # Init the button
    event_data['button'] = Pin("BUTTON1", Pin.IN, Pin.PULL_UP)
    # Init the mag sensor
    event_data['mag_sensor'] = Pin("MAG1", Pin.IN, Pin.PULL_NONE)
    # Init BLE
    canvas_ble.init()
    canvas_ble.set_periph_callbacks(ble_connect, ble_disconnect)
    devid = canvas_ble.addr_to_str(canvas_ble.my_addr())[10:12] + canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14]
    event_data['ble_name'] = config['ble_name'] + "-" + devid
    event_data['adv'] = canvas_ble.Advertiser()
    #event_data['adv'].set_phys(canvas_ble.PHY_1M, canvas_ble.PHY_1M)
    event_data['adv'].set_properties(True, False, True)
    event_data['adv'].set_interval(config["reporting_interval_ms"], config["reporting_interval_ms"] + 10)
    event_data['adv'].clear_buffer(False)
    event_data['adv'].add_ltv(0x01, bytes([0x06]), False)
    event_data['adv'].add_tag_string(0x09, event_data['ble_name'], False)
    event_data['adv'].add_ltv(0xff, event_data['hdr'] + b"\xb00\xb00\xb00\xb00\xb00\xb00\x00", False)
    event_data['adv'].add_canvas_data(0, config['network_id'], False)
    # Start BLE Advertising
    event_data['adv'].start()
    # Print help text
    print(' \r\n\r\nBT610 AC Current sensor script ' + app_ver)
    print('------------------------------------')
    print("          BLE Name: " + event_data['ble_name'])
    print('Reporting Interval: ' + str(config["reporting_interval_ms"]) + 'ms')
    #print('Press ctrl-c within 15 seconds to access the REPL and cancel low power mode\r\n')
    #time.sleep_ms(15000)
    #print('Entering low power mode, UART REPL will turn off in 20 seconds...\r\n')
    # Start countdown to disable REPL UART
    #machine.console_sleep()

def read_ac_current(channel):

    # Read the current sense value for AIN1, assuming a 20A sensor
    rv = read_current_sense(channel, 20, 10)
    adc_value = rv[0]
    
    if console_display_enabled:
        voltage_times_1000 = rv[1]
        amps_rms_times_1000 = rv[2]

        # Convert ADC input voltage to a string for printing
        vstring = str(voltage_times_1000)[0:-3]
        if voltage_times_1000 is 0:
            vstring = "0"
        
        # Convert AC current to a string for printing
        astring = str(amps_rms_times_1000)[0:-3]
        if amps_rms_times_1000 is 0:
            astring = "0"

        print("\033[K\r\n\033[KAC Current Sensor - AIN" + str(channel) + " (20A)")
        print("\033[K------------------------------")
        print("\033[K  ADC Value: ", adc_value)
        print("\033[K  ADC Volts: ", vstring + '.' + str(voltage_times_1000)[-3:], "V")
        print("\033[K AC Current: ", astring + '.' + str(amps_rms_times_1000)[-3:], "Amps RMS")
        print("\033[K")

    return adc_value

init_application()
timer = canvas.Timer(config["reporting_interval_ms"], True, timer_callback, event_data)
timer.start()

print('\r\n\r\nNOTE: This script requires Canvas Firmware v2.0.0 or later.')
print('\r\n\r\nThis script is designed for use with an AC current transducer with 5V output and 20A rating.')
print('Connect the positive "+" terminal to AIN1 and the negative "-" terminal to GND on the BT610.')
print('Be sure to clamp the current sensor around a "hot" wire carrying AC current before taking a measurement.')
print('\r\nConfiguration can be set using the "config" object.\r\nTo view configuration parameters: config <ENTER>\r\nTo set a parameter: config["reporting_interval_ms"] = 1000 <ENTER>\r\nTo save the configuration: save_config() <ENTER>, then Ctrl+D to restart the device.\r\n')
print('To display current data to the console, type "console_display_enabled = True" <ENTER>')
print('To stop displaying current data to the console, type "console_display_enabled = False" <ENTER>\r\n')

