# BLE to MQTT Gateway
#
# Starter project with BLE ad filtering and sensor data publishing via MQTT.
# This project is designed as the basis of a simple BLE to MQTT Gateway 
# application for use with the Veda SL917 SoC Explorer board (brd2911a).
#
# The scan filter is set up to receive BLE ads from Sentrius BT510 sensors
# running the Canvas BT510 beacon demo. The MQTT client is set up to publish
# all sensor data to a configurable topic with format:
#   <mqtt_publish_topic>/<ble_device_mac_address>
from state_machine import StateMachine
from mqtt_client import MQTTClient
from sntp_client import Sntp
from config import Config
from canvas import Timer
import canvas_ble as ble
import os, sys, machine, gc, time, struct, network

# State machine for the Wi-Fi based BLE to MQTT gateway
class WifiBleToMqtt(StateMachine):
    # List of events that the state machine can handle
    _events = ['tick_event', 'wifi_started_event', 'mqtt_started_event', 'mqtt_disconnect_event']
    # Initial state of the state machine
    _start = 'idle_state'

    def __init__(self, app):
        super().__init__()
        self.app = app
    
    # [IDLE STATE] - Waiting for required configuration to be set
    def idle_state(self, event):
        if event == 'tick_event':
            # Check if the configuration is valid
            if self.app.is_config_valid():
                print('\r\n(tick) -> [Idle]')
                app.config_invalid_banner_shown = False
                # Display the configuration (skipping passwords/passphrases)
                print('Configuration:')
                for key in self.app.required_config_keys:
                    if (key != 'mqtt_password') and (key != 'wifi_passphrase'):
                        print('  ' + key + ': ' + str(self.app.config.get(key)))
                # Initialize the WLAN interface
                self.app.init_wlan()
                # Initialize BLE
                ble.init()
                self._set('wifi_disconnected_state') # Transition to the Wi-Fi disconnected state to attempt a Wi-Fi network join
            else:
                if app.config_invalid_banner_shown == False:
                    app.config_invalid_banner_shown = True
                    print('\r\nInvalid configuration')
                    print('Use "app.config.set(<key>,<value>)" to set parameters and call "app.config.save()" to save them\r\n')

    # [WIFI DISCONNECTED STATE] - Waiting for a Wi-Fi connection
    def wifi_disconnected_state(self, event):
        if event == 'tick_event':
            print('\r\n(tick) -> [Wi-Fi disconnected]')
            if self.app.state_tick_timer.get_interval() != self.app.state_tick_slow_ms:
                print('State machine timer interval set to ' + str(self.app.state_tick_slow_ms) + 'ms')
                self.app.state_tick_timer.change_period(self.app.state_tick_slow_ms)
        self.app.led1.off()

        # Make sure the MQTT client is disconnected and cleaned up
        if self.app.mqtt_client is not None:
            if self.app.mqtt_client.sock is not None:
                self.app.mqtt_client.sock.close() # Close the socket if it exists
                self.app.mqtt_client = None
        
        # Attempt to connect to the Wi-Fi network
        try:
            print('Connecting to Wi-Fi...')
            self.app.wlan.active(True)
            ret = self.app.wlan.connect(self.app.config.get('wifi_ssid'), self.app.config.get('wifi_passphrase'))
            if self.app.wlan.isconnected():
                self._set('wifi_connected_state') # Transition to the Wi-Fi connected state
                self.wifi_started_event()
            else:
                print('Failed to connect to Wi-Fi (return code: ' + str(ret) + ')')
        except Exception as e:
            print('Failed to connect to Wi-Fi, retrying... (' + str(e) + ')')

    # [WIFI CONNECTED STATE] - Waiting for an MQTT connection
    def wifi_connected_state(self, event):
        if event == 'tick_event':
            print('\r\n(tick) -> [Wi-Fi connected]')
        self.app.led1.on()
        gc.collect() # Run garbage collection to free up memory

        if event == 'wifi_started_event':
            print('\r\n(wifi_started) -> [Wi-Fi connected]')
            if self.app.state_tick_timer.get_interval() != self.app.state_tick_slow_ms:
                print('State machine timer interval set to ' + str(self.app.state_tick_slow_ms) + 'ms')
                self.app.state_tick_timer.change_period(self.app.state_tick_slow_ms)
        
        if event == 'mqtt_disconnect_event':
            print('\r\n(mqtt_disconnect) -> [Wi-Fi connected]')
            self.app.mqtt_client = None
            self.app.led0.off()
        
        # Attempt to setup the SNTP client
        if self.app.sntp_client is None:
            try:
                # Create the SNTP client, poll the NTP server and set the RTC
                self.app.sntp_client = SntpClient(self.app.config)
            except Exception as e:
                # SNTP client failed, set RTC to 0 and continue without it
                print('SNTP client unavailable (' + str(e) + '), continuing without it...')
                machine.RTC().datetime(time.gmtime(0))

        # Attempt to connect to the MQTT broker. If TLS credentials
        # are configured, attempt to use them to connect.
        gc.collect() # Run garbage collection to free up memory
        if self.app.config.get('mqtt_client_cert_file') is not None and \
            self.app.config.get('mqtt_client_key_file') is not None and \
            self.app.config.get('mqtt_ca_cert_file') is not None:
            # TLS credentials are configured, use them to connect to the MQTT broker
            print('Connecting to MQTT broker (With TLS)...')
            ca_cert = None
            client_cert = None
            client_key = None
            try:
                f = open(self.app.config.get('mqtt_ca_cert_file'), 'rb')
                ca_cert = f.read()
                f.close()
            except:
                print('Failed to load CA cert file')
                raise
            try:
                f = open(self.app.config.get('mqtt_client_cert_file'), 'rb')
                client_cert = f.read()
                f.close()
            except:
                print('Failed to load client cert file')
                raise
            try:
                f = open(self.app.config.get('mqtt_client_key_file'), 'rb')
                client_key = f.read()
                f.close()
            except:
                print('Failed to load client key file')
                raise
            print('Starting MQTT Client (TLS)...')
            self.app.mqtt_client = MQTTClient(
                self.app.config.get('mqtt_client_id'),
                self.app.config.get('mqtt_hostname'),
                port=self.app.config.get('mqtt_port'),
                keepalive=self.app.config.get('mqtt_keepalive'),
                ssl=True,
                ssl_params={
                    'cert': client_cert,
                    'key': client_key,
                    'cadata': ca_cert,
                    'server_hostname': self.app.config.get('mqtt_hostname')
                }, debug=False)
            gc.collect() # Run garbage collection to free up memory
        else:
            print('Connecting to MQTT broker (No TLS)...')
            self.app.mqtt_client = MQTTClient(
                self.app.config.get('mqtt_client_id'),
                self.app.config.get('mqtt_hostname'),
                port=self.app.config.get('mqtt_port'),
                user=self.app.config.get('mqtt_user'),
                password=self.app.config.get('mqtt_password'),
                keepalive=self.app.config.get('mqtt_keepalive'),
                debug=False)
        
        if self.app.mqtt_client is not None:
            try:
                self.app.mqtt_client.connect(True)           # Connect to the MQTT broker with a clean session
                print('Connected to MQTT broker')
                self.app.mqtt_ping_time_ms = time.ticks_ms() # Restart the MQTT ping timer
                self.app.mqtt_ping_fail_count = 0            # Count indicating # of times a ping response is not received
                self._set('mqtt_connected_state')            # Transition to the MQTT Connected state
                self.mqtt_started_event()
            except Exception as e:
                if self.app.mqtt_client.sock is not None:
                    self.app.mqtt_client.sock.close()
                self.app.mqtt_client = None
                print('MQTT connect failed (' + str(e) + '), retrying...')

    # [MQTT CONNECTED STATE] - Scanning for BLE devices and publishing data over MQTT
    def mqtt_connected_state(self, event):
        if event == 'mqtt_started_event':
            print('\r\n(mqtt_started) -> [MQTT connected]')
            # Start scanning for BLE devices
            self.app.ble_scanner.start_scan()

        if event == 'mqtt_disconnect_event':
            print('[MQTT connected] -> (mqtt_disconnect)')
            # Stop scanning for BLE devices on MQTT disconnect event
            self.app.ble_scanner.stop_scan()
            self._set('wifi_connected_state') # Transition back to the Wi-Fi connected state (to retry MQTT connection)
            self.mqtt_disconnect_event()

        self.app.led0.on()
        if event == 'tick_event':
            # Remove any BLE devices that have not been seen for more than 120 seconds
            for device in self.app.ble_device_db.devices.values():
                if not 'last_seen' in device:
                    device['last_seen'] = time.time()
                delta = (time.time() - device['last_seen'])
                if delta > 120:
                    addr_str = ble.addr_to_str(device['raw_ad'].addr)
                    print('Removing device: ' + addr_str + ' last_seen: ' + str(device['last_seen']) + ' (time: ' + str(time.time()) + ', delta: ' + str(delta) + ')')
                    del self.app.ble_device_db.devices[addr_str]
            print('\r\n(tick) -> [MQTT connected] (BLE devices: ' + str(len(self.app.ble_device_db.devices)) + ', Mem Free: ' + str(gc.mem_free()) + ', Time: ' + str(time.time()) + ')')
            gc.collect() # Run garbage collection to free up memory
            # Check if the MQTT client is still connected by detecting ping failures.
            if self.app.mqtt_ping_fail_count >= 3:
                print('MQTT ping failed, disconnecting...')
                self._set('wifi_connected_state') # Transition back to the Wi-Fi connected state (to retry MQTT connection)
                self.mqtt_disconnect_event()
                return
            else:
                try:
                    # Publish the BLE device data to the MQTT broker
                    for v in self.app.ble_device_db.devices.values():
                        self.app.publish_ble_device(v)
                except Exception as e:
                    print('MQTT publish failed (' + str(e) + '), disconnecting...')
                    self._set('wifi_connected_state') # Transition back to the Wi-Fi connected state (to retry MQTT connection)
                    self.mqtt_disconnect_event()
                    return

            # Ping the MQTT broker to keep the connection alive
            if abs(time.ticks_ms() - self.app.mqtt_ping_time_ms) >= self.app.config.get('mqtt_keepalive') * 700:
                self.app.mqtt_ping_time_ms = time.ticks_ms()
                if self.app.mqtt_client is not None:
                    try:
                        print('  MQTT ping TX')
                        self.app.mqtt_client.ping()
                        # Wait for the ping response
                        if self.app.mqtt_client.wait_msg(5000) is None:
                            # expected behavior, ping response returns None
                            print('  MQTT ping RX')
                            self.app.mqtt_ping_fail_count = 0 # Reset the ping fail counter
                    except Exception as e:
                        print('  MQTT no response: {}'.format(str(e)))
                        # MQTT ping failure indicates the client is not connected
                        self.app.mqtt_ping_fail_count += 1
                else:
                    # MQTT ping failure indicates the client is not connected
                    print('  No MQTT Client, can\'t ping')
                    self.app.mqtt_ping_fail_count += 1

# In-memory database for BLE devices and their data
class BleDeviceDb:
    def __init__(self):
        self.db_lock = False
        self.devices = {}
    
    # Add/Update the device and data in the database
    def update_device(self, addr_str, evt):
        if addr_str not in self.devices:
            self.devices[addr_str] = {}
        self.devices[addr_str]['raw_ad'] = evt
        self.devices[addr_str]['last_seen'] = time.time()
    
# BLE scanner class for scanning and filtering BLE devices
class FilteredScanner(ble.Scanner):
    def __init__(self, app):
        super().__init__(self.scan_cb)
        self.app = app
        self.setup_ble_scan_filters()
        self.is_scanning = False
        # IMPORTANT: Setting the scan window to a high (>50%) duty cycle will
        # increase power consumption and may interfere with Wi-Fi operations.
        # Tune these values to your application's needs based on the expected
        # BLE advertising interval of the target devices.
        self.scan_window_ms = 50    # scan window
        self.scan_interval_ms = 500 # scan interval
        self.set_timing(self.scan_interval_ms, self.scan_window_ms) # Set the scan timing

    def setup_ble_scan_filters(self):
        # BT510 canvas beacon sample uses '7700' for company ID and 'C900' for protocol id
        self.filter_add(ble.Scanner.FILTER_MANUF_DATA, bytes.fromhex('7700C900')) # Set up the BLE scan filter

    def start_scan(self):
        if not self.is_scanning:
            try:
                self.start(0)            # Start scanning (passive)
                self.is_scanning = True  # Update scanning state
                print(  'BLE scan started')
            except Exception as e:
                print('BLE scan start failed (' + str(e) + ')')

    def stop_scan(self):
        if self.is_scanning:
            try:
                self.stop()              # Stop scanning
                self.is_scanning = False # Update scanning state
                print(  'BLE scan stopped')
            except Exception as e:
                print('BLE scan stop failed (' + str(e) + ')')

    def scan_cb(self, evt):
        self.app.handle_ble_ad(evt) # Handle the scan result

# SNTP client class for synchronizing time with an SNTP server (optional)
class SntpClient:
    def __init__(self, config):
        self.timer = None
        self.sntp = None
        self.hostname = None

        # Save the configuration
        if 'sntp_hostname' in config.config:
            self.hostname = config.get('sntp_hostname')
        if 'sntp_period' in config.config:
            self.period = config.get('sntp_period')
        else:
            self.period = 3600

        # Create the SNTP client
        if self.hostname is None:
            # Use default SNTP server
            print('Using default SNTP server')
            self.sntp = Sntp()
        else:
            # Use specified SNTP server
            print('Using SNTP server: ' + self.hostname)
            self.sntp = Sntp(host=self.hostname)

        # Initial poll
        self.poll(None)

    def poll(self, data):
        try:
            print('  SNTP poll...')
            self.sntp.poll()
        except Exception as e:
            print('SNTP poll failed:', e)
        if self.timer is None:
            self.timer = Timer(self.period * 1000, True, self.poll, None)
            self.timer.start()

# The main application class
class App:
    app_id = 'wifi_ble_to_mqtt'
    app_ver = '0.1.0'

    def __init__(self):
        self.print_app_info()              # Display app info
        self.config = Config()             # Create the config object
        self.config.load()                 # Load the configuration file
        self.ble_device_db = BleDeviceDb() # Create the in-memory database for BLE devices
        self.wlan = None                   # WLAN interface is initially None
        self.sntp_client = None            # SNTP client is initially None
        self.mqtt_client = None            # MQTT client is initially None
        self.state_tick_timer = None       # State tick timer is initially None
        self.mqtt_ping_fail_count = 0      # Counts when a ping response is not received
        self.ble_scanner = FilteredScanner(self) # Create the BLE scanner
        self.state_machine = WifiBleToMqtt(self) # Create the state machine
        self.config_invalid_banner_shown = False # Flag to indicate if invalid config banner has been shown
        self.mqtt_ping_time_ms = 0         # Counter for MQTT ping
        self.state_tick_fast_ms = 100      # State tick timer interval in ms (for fast events)
        self.state_tick_slow_ms = 10000    # State tick timer interval in ms (for slow events)
        self.delta_temp = 1.0              # Temperature delta for publishing
        self.delta_accel = 16              # Acceleration delta for publishing
        self.publish_period_ms = 60000     # Minimum publish period in ms
        self.print_period_ms = 10000       # Minimum print period in ms
        self.led0 = machine.Pin('LED0', machine.Pin.OUT, machine.Pin.PULL_NONE) # LED0 pin
        self.led0.off()
        self.led1 = machine.Pin('LED1', machine.Pin.OUT, machine.Pin.PULL_NONE) # LED1 pin
        self.led1.off()

    def state_machine_tick_cb(self, data):
        self.state_machine.tick_event()

    def print_app_info(self):
        print('System:', os.uname().sysname, '\r\nBoard:',
        os.uname().machine, '\r\nBuild:', os.uname().release)
        print('App ID:', self.app_id, '\r\nApp Version:', self.app_ver)

    def init_wlan(self):
        self.wlan = network.WLAN(network.WLAN.IF_STA)

    def start_state_machine(self):
        self.state_tick_timer = Timer(self.state_tick_fast_ms, True, self.state_machine_tick_cb, None)
        self.state_tick_timer.start() # Start the state machine tick timer
    
    def stop(self):
        # Stop the state machine tick timer
        if self.state_tick_timer is not None:
            self.state_tick_timer.stop()
        # Stop the BLE scanner
        self.ble_scanner.stop_scan()

    def is_config_valid(self):
        # If this boot had an invalid configuration, always return False
        if app.config_invalid_banner_shown:
            return False
        # Check if the configuration is valid
        self.required_config_keys = ['mqtt_client_id', 'mqtt_hostname', 'mqtt_port',
            'mqtt_user', 'mqtt_password', 'mqtt_keepalive', 
            'mqtt_publish_topic', 'wifi_ssid', 'wifi_passphrase']
        for key in self.required_config_keys:
            if key not in self.config.config:
                print('Missing required config key: {}'.format(key))
                return False
        return True
    
    def handle_ble_ad(self, evt):
        # Update the device in the database
        self.ble_device_db.update_device(ble.addr_to_str(evt.addr), evt)
        # Toggle LED0 state to indicate a BLE advertisement was received
        self.led0.toggle()
        time.sleep_ms(10)
        self.led0.toggle()
    
    def publish_ble_device(self, entry):
        # Get manufacturer-specific data from the advertisement
        m = ble.find_ltv(0xff, entry['raw_ad'].data)
        if m is None:
            return

        # Get the name from the ad
        name = 'BT510'
        nm = ble.find_ltv(0x09, entry['raw_ad'].data)
        if nm is not None:
            name = nm[1:].decode()

        # Get the temperature from the manufacturer-specific data
        temp_bytes = m[12:14]
        temp_val = float(struct.unpack('>h', temp_bytes)[0])
        tempc = (((temp_val * 175720)/65536) - 46850) / 1000

        # Get the accel x,y,z values from the ad as 8 bit signed values
        ax = struct.unpack('b', m[5:6])[0]
        ay = struct.unpack('b', m[7:8])[0]
        az = struct.unpack('b', m[9:10])[0]

        # Get the sequence counter from the ad
        seq = m[10] & 0xFF

        # Get battery voltage from the ad
        try:
            battmv = struct.unpack('>H', m[14:16])[0]
        except:
            battmv = 0 # for devices that do not contain this field
            pass

        # Get device status flags from the ad
        flags = m[11] & 0xFF

        # Check if we should publish
        publish = False
        ble_addr = ble.addr_to_str(entry['raw_ad'].addr)
        if 'last_print' not in self.ble_device_db.devices[ble_addr]:
            self.ble_device_db.devices[ble_addr]['last_print'] = 0
            publish = True
        elif abs(tempc - self.ble_device_db.devices[ble_addr]['tempc']) >= self.delta_temp:
            publish = True
        elif self.ble_device_db.devices[ble_addr]['flags'] != flags:
            publish = True
        elif abs(ax - self.ble_device_db.devices[ble_addr]['ax']) >= self.delta_accel:
            publish = True
        elif abs(ay - self.ble_device_db.devices[ble_addr]['ay']) >= self.delta_accel:
            publish = True
        elif abs(az - self.ble_device_db.devices[ble_addr]['az']) >= self.delta_accel:
            publish = True
        elif abs(time.ticks_ms() - self.ble_device_db.devices[ble_addr]['last_publish']) >= self.publish_period_ms:
            publish = True

        # Print if necessary
        if publish or (time.ticks_ms() - self.ble_device_db.devices[ble_addr]['last_print']) >= self.print_period_ms:
            print('Device: {}, Name: {}, Accel: ({}, {}, {}), Seq: {}, Flags: {}, TempC: {}, BattMv: {}'.format(
                ble_addr, name, ax, ay, az, seq, flags, tempc, battmv))
            self.ble_device_db.devices[ble_addr]['last_print'] = time.ticks_ms()

        # Publish if necessary
        if publish:
            # Publish the BLE device data to the MQTT broker
            topic = self.config.get('mqtt_publish_topic') + '/' + ble_addr
            print('  publishing to topic: ' + topic)
            # Toggle LED1 state to indicate a BLE advertisement was published
            self.led1.toggle()
            time.sleep_ms(50)
            self.led1.toggle()
            self.mqtt_client.publish(topic, '{{"ts": {}, "deviceid": "{}", "name": "{}", "board": "bt510", "ax": {}, "ay": {}, "az": {}, "flags": {}, "tempc": {}, "battmv": {}}}'.format(time.time(), ble_addr, name, ax, ay, az, flags, tempc, battmv))
            self.ble_device_db.devices[ble_addr]['last_publish'] = time.ticks_ms()
            self.ble_device_db.devices[ble_addr]['tempc'] = tempc
            self.ble_device_db.devices[ble_addr]['flags'] = flags
            self.ble_device_db.devices[ble_addr]['ax'] = ax
            self.ble_device_db.devices[ble_addr]['ay'] = ay
            self.ble_device_db.devices[ble_addr]['az'] = az
            self.ble_device_db.devices[ble_addr]['battmv'] = battmv
            self.ble_device_db.devices[ble_addr]['seq'] = seq
            self.ble_device_db.devices[ble_addr]['name'] = name

app = App()
app.start_state_machine()
