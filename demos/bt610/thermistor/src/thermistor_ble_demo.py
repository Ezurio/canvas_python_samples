app_id='thermistor_ble_demo'
app_ver='1.0.0'

import canvas
import canvas_ble
from machine import ADC
from machine import I2C
from machine import Pin
import machine
import time
import math
import struct

io_expander = None
io_expander_reset = None
io_expander_address = 0x70
analog_enable = None
therm_enable = None
adc = None
adc_power = None
led1 = None
led2 = None
AIN1 = 1
AIN2 = 2
AIN3 = 3
AIN4 = 4
config = { }
event_data = { }
event_data['ctr'] = 0
event_data['hdr'] = b'\x77\x00\xcd\x00'
console_display_enabled = False

def load_config():
    global config

    # Set default configuration values
    config['reporting_interval_ms'] = 1000
    config['ble_name'] = 'BT610-TH'
    config['network_id'] = 0xffff
    config['th1_enabled'] = 1
    config['th2_enabled'] = 0
    config['th3_enabled'] = 0
    config['th4_enabled'] = 0
    
    # Load configuration from a file
    try:
        f = open('config.cb', 'rb')
    except:
        print('Configuration file not found, saving defaults')
        save_config()
        return
    
    # Read the entire file
    cbor = f.read()
    f.close()
    if cbor is None:
        print('Configuration file is empty, saving defaults')
        save_config()
        return
    
    # Convert CBOR to an object
    config_file = canvas.zcbor_to_obj(cbor)
    if config_file is None:
        print('Configuration is corrupt, saving defaults')
        save_config()
        return
    
    # Copy the configuration from the file
    for c in config_file:
        config[c] = config_file[c]

def save_config():
    global config

    config_file = { }

    # Copy config values from the live config object
    config_file['reporting_interval_ms'] = config['reporting_interval_ms']
    config_file['ble_name'] = config['ble_name']
    config_file['network_id'] = config['network_id']
    config_file['th1_enabled'] = config['th1_enabled']
    config_file['th2_enabled'] = config['th2_enabled']
    config_file['th3_enabled'] = config['th3_enabled']
    config_file['th4_enabled'] = config['th4_enabled']

    # Convert the configuration to CBOR
    cbor = canvas.zcbor_from_obj(config_file, 0)
    if cbor is None:
        print('Unable to convert configuration to CBOR')
        return
    
    # Write the CBOR to a file
    f = open('config.cb', 'wb')
    if f is None:
        print('Unable to open configuration file')
        return
    
    size = f.write(cbor)
    f.close()

def ble_connect(conn):
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))

def ble_disconnect(conn):
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    event_data['adv'].start()

def timer_callback(event):
    flags = 0x06

    if console_display_enabled:
        print('\r\033[37A')

    # Read the thermistor values for TH1-TH4
    sample = read_temperature(AIN1)
    sample_bytes = struct.pack('>f', sample[0]) # Pack the float value into bytes (big-endian format)
    
    sample = read_temperature(AIN2)
    sample_bytes += struct.pack('>f', sample[0]) # Pack the float value into bytes (big-endian format)
    
    sample = read_temperature(AIN3)
    sample_bytes += struct.pack('>f', sample[0]) # Pack the float value into bytes (big-endian format)
    
    sample = read_temperature(AIN4)
    sample_bytes += struct.pack('>f', sample[0]) # Pack the float value into bytes (big-endian format)

    if console_display_enabled:
        print('\033[KInternal Reference')
        print('\033[K------------------------------')
        print('\033[K        VDD: ', sample[1], 'V')
        print('\033[K')

    sample_bytes += struct.pack('>f', sample[1]) # Pack VDD as float value into bytes (big-endian format)

    # Read the mag sensor
    if event_data['mag_sensor'].value():
        flags &= ~0x02
    # Read the button
    if event_data['button'].value():
        flags &= ~0x04
    # Upper 4 bits indicate ADC channels that are enabled (via local config)
    if(config.get('th1_enabled') == 1):
        flags |= 0x10
    if(config.get('th2_enabled') == 1):
        flags |= 0x20
    if(config.get('th3_enabled') == 1):
        flags |= 0x40
    if(config.get('th4_enabled') == 1):
        flags |= 0x80
    # Update BLE Advertisement
    event['adv'].clear_buffer(False)
    event['adv'].add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([0x06]), False)
    event['adv'].add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, event['ble_name'], False)
    event['adv'].add_ltv(canvas_ble.AD_TYPE_MANU_SPECIFIC, event_data['hdr'] + sample_bytes + bytes([event['ctr'] & 0xFF, flags]), False)
    event['adv'].update()
    event['ctr'] = event['ctr'] + 1

def init_leds():
    global led1, led2
    # Pin identified by gpio-dynamic label (device tree)
    led1 = Pin('LED1', Pin.OUT, 0)
    led1.off()

    # Pin identified by gpio-dynamic label (device tree)
    led2 = Pin('LED2', Pin.OUT, 0)
    led2.off()

def init_io_expander():
    global io_expander
    global io_expander_reset
    global io_expander_address

    io_expander = I2C('i2c@40003000', io_expander_address)
    io_expander_reset = Pin(('gpio@50000000', 28), Pin.OUT, Pin.PULL_NONE)

    # Reset the IO expander
    io_expander_reset.low()
    time.sleep_ms(1)
    io_expander_reset.high()
    time.sleep_ms(1)

def init_analog_enable():
    global analog_enable
    analog_enable = Pin(('gpio@50000300', 13), Pin.OUT, Pin.PULL_NONE)
    analog_enable.low() # disables analog circuit power

def init_therm_enable():
    global therm_enable
    therm_enable = Pin(('gpio@50000000', 10), Pin.OUT, Pin.PULL_NONE)
    therm_enable.high() # disables thermistor circuit power, therm_enable is active low

def setup_for_thermistor():
    global adc
    global adc_power

    # Setup ADC object to sample channel SIO_02/AIN0 of SoC (Labeled ADC_IN1 on BT610)
    # Setup ADC object to sample channel SIO_03/AIN1 of SoC (Labeled ADC_IN2 on BT610)
    adc = ADC(2) # AIN1 is used for for Thermistor Sensing (channel 2)
    # setup sample for 40000us (25Hz), attenuation of 4 (1/4), scale of 1 (no gain)
    adc.init(sample_ns=40000, atten=4, gain=1, reference=ADC.REF_VDD)

    adc_power = ADC(9) # Used to sample internal reference voltage (VDD)
    adc_power.init(sample_ns=40000, atten=6, gain=1, reference=ADC.REF_INTERNAL)

    # Setup port expander AIN address and port select pins as outputs
    # Register 3, 0b1 configures high impedance input, 0b0 configures as output
    # 0b11xxxxxx sets AUX1,AUX2 as inputs
    # 0bxx000000 sets AIN1,AIN2,AIN3,AIN4,AIN_A0,AIN_A1 as outputs
    io_expander.write(bytes([3,0b11000000]))

def read_thermistor(channel, samples_to_average=10):
    # Disable the Analog sense circuit power
    analog_enable.low()

    # Enable VREF for thermistor (active low)
    therm_enable.low()

    time.sleep_us(200) # wait 200uS for analog switch startup/settling

    # Select the AINx input path by setting AIN_A0/AIN_A1 via io expander
    # Register 1, 0b0 output low, 0b1 output high. AIN1,AIN0 in bits 0b00xx0000
    mux_sel = (((channel - 1) & 0x03) << 4)
    io_expander.write(bytes([1, mux_sel])) # thermistor setup

    # Wait another 100us before starting to take samples
    time.sleep_us(100) # wait 100uS for analog switch startup/settling

    # Wait 100ms before sampling the ADC
    time.sleep_ms(100)

    # Perform samples_to_average ADC reads and average the result
    adc_value = 0
    adc_accum = 0
    for i in range(samples_to_average):
        adc_value = adc.read_u16()
        adc_accum += adc_value
    adc_value = adc_accum // samples_to_average

    # Disable VREF for thermistor
    therm_enable.high()

    # Read the ADC power value (AIN0)
    adc_power_value = adc_power.read_uv()

    # Convert to Vref
    vref = adc_power_value / 1000000.0 # Convert to volts

    # Convert the ADC value to ohms resistance
    # NOTE: ge and oe values are used to calibrate the ADC value to ohms resistance.
    #       default values are used here for testing purposes. In production, these values should be 
    #       replaced with measured/calibrated values. To read more about the ADC calibration procedure,
    #       refer to https://www.ezurio.com/documentation/application-note-bt610-thermistor-adc-calibration
    #
    ge = 1.0 # ADC calibration gain error (replace this with a measured/calibrated value here for production)
    oe = 0.0 # ADC calibration offset error (replace this with a measured/calibrated value here for production)
    adc_value = int((adc_value - oe) / ge)                 # Apply calibration errors to ADC value
    rpullup = 10000.0                                      # Pullup resistor value (10K) on the BT610 thermistor inputs
    adc_range = 65535.0                                    # ADC range (16-bit)
    rtherm = (adc_value * rpullup) / (adc_range - adc_value) # Convert ADC value to ohms resistance

    # Constants for the Steinhart-Hart Equation */
    THERMISTOR_S_H_A = 1.132e-3
    THERMISTOR_S_H_B = 2.338e-4
    THERMISTOR_S_H_C = 8.780e-8
    THERMISTOR_S_H_OFFSET = 273.15

    # Calculate the temperature in Celsius using the Steinhart-Hart equation
    try:
        ln = math.log(rtherm)
        tempK = 1.0 / ( THERMISTOR_S_H_A + THERMISTOR_S_H_B * ln + THERMISTOR_S_H_C * ln * ln * ln )
    except:
        tempK = THERMISTOR_S_H_OFFSET
        print('Error calculating temperature, using default value')
    tempC = tempK - THERMISTOR_S_H_OFFSET # Convert from K to C
    return [adc_value, tempC, vref]

def init_application():
    global event_data

    # Initialize the LEDs
    init_leds()

    # Load configuration
    load_config()

    # Initialize the IO expander, analog enable pin, and ADC peripheral
    init_io_expander()
    init_analog_enable()
    init_therm_enable()

    # Initialize the analog chain for thermistor sensing
    setup_for_thermistor()

    # Init the button
    event_data['button'] = Pin('BUTTON1', Pin.IN, Pin.PULL_UP)
    # Init the mag sensor
    event_data['mag_sensor'] = Pin('MAG1', Pin.IN, Pin.PULL_NONE)
    # Init BLE
    canvas_ble.init()
    canvas_ble.set_periph_callbacks(ble_connect, ble_disconnect)
    devid = canvas_ble.addr_to_str(canvas_ble.my_addr())[10:12] + canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14]
    event_data['ble_name'] = config['ble_name'] + '-' + devid
    event_data['adv'] = canvas_ble.Advertiser()
    #event_data['adv'].set_phys(canvas_ble.PHY_1M, canvas_ble.PHY_1M)
    event_data['adv'].set_properties(True, False, True)
    event_data['adv'].set_interval(config['reporting_interval_ms'], config['reporting_interval_ms'] + 10)
    event_data['adv'].clear_buffer(False)
    event_data['adv'].add_ltv(0x01, bytes([0x06]), False)
    event_data['adv'].add_tag_string(0x09, event_data['ble_name'], False)
    event_data['adv'].add_ltv(0xff, event_data['hdr'] + b'\xb00\xb00\xb00\xb00\xb00\xb00\x00', False)
    event_data['adv'].add_canvas_data(0, config['network_id'], False)
    # Start BLE Advertising
    event_data['adv'].start()
    # Print help text
    print(' \r\n\r\nBT610 Thermistor sensor script ' + app_ver)
    print('------------------------------------')
    print('          BLE Name: ' + event_data['ble_name'])
    print('Reporting Interval: ' + str(config['reporting_interval_ms']) + 'ms')

def read_temperature(channel):
    # Read the thermistor value for AIN1
    rv = read_thermistor(channel, 10) # 10 samples to average
    adc_value = rv[0] # raw ADC value (0-65535)
    temperature_value = rv[1] # temperature in C
    vref = rv[2] # Vref in volts

    if console_display_enabled:
        # Check if the channel is enabled in the config
        ch_enabled = 'Enabled'
        if config['th' + str(channel) + '_enabled'] == 0:
            ch_enabled = 'Disabled'
        print('\033[KThermistor - TH' + str(channel) + ' (' + ch_enabled + ' in BLE advertisement, set by config)')
        print('\033[K------------------------------')
        print('\033[K  ADC Value: ', adc_value, 'counts')
        print('\033[KTemperature: ', temperature_value, 'C')
        print('\033[K')

    return [temperature_value, vref]


init_application()
timer = canvas.Timer(config['reporting_interval_ms'], True, timer_callback, event_data)
timer.start()

print('\r\n\r\nNOTE: This script requires Canvas Firmware v2.0.0 or later.')
print('\r\n\r\nThis script is designed for use with a 10K Thermistor.')
print('Connect the thermistor leads to TH1 and GND on the BT610. If present, connect the cable shield to GND.')
print('\r\nConfiguration can be set using the "config" object.\r\nTo view configuration parameters: config <ENTER>\r\nTo set a parameter: config["reporting_interval_ms"] = 1000 <ENTER>\r\nTo save the configuration: save_config() <ENTER>, then Ctrl+D to restart the device.\r\n')
print('To display data to the console, type "console_display_enabled = True" <ENTER>')
print('To stop displaying data to the console, type "console_display_enabled = False" <ENTER>\r\n')

print('Press ctrl-c within 15 seconds to access the REPL and cancel low power mode\r\n')
try:
    time.sleep_ms(15000)
    print('Entering low power mode, UART REPL will be disabled until next reset...\r\n')
    # Start countdown to disable REPL UART
    machine.console_sleep(1000)
except:
    print('Low power mode canceled, UART REPL enabled\r\nNOTE: This mode is intended for development use only.\r\n')
    pass
