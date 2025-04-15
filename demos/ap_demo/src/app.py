import sys
import os
import gc
import time
import json
import binascii
import canvas_ble
import machine
import canvas
from machine import Pin
from machine import I2C
from ap import Ap
from station import Station
from httpserver import HttpServer
from mqtt import MQTTClient
from temphum4 import TempHum4Click
from webhook import WebHook
from mqtt import MQTTException
from mqtt import TimeoutException

class App:
    app_id = 'veda_sl917_explorer_board_ap_demo'
    app_ver = '0.2.2'
    fmt_cyan = "\x1b[1;38;5;87m"
    fmt_green = "\x1b[38;5;231;48;5;28m"
    fmt_stop = "\x1b[0m"
    fmt_red = "\x1b[1;38;5;231;48;5;88m"
    fmt_white = "\x1b[1;38;5;231m"
    fmt_amber = "\x1b[1;38;5;214m"
    fmt_dark = "\x1b[38;5;236;48;5;235m"

    def __init__(self):
        self.config = {}
        self.network_list = []
        self.ble_scan_result_list = []
        self.whook = None
        self.mqtt = None
        self.th4click = None
        self.do_ble_scan = False
        self.new_ble_scan_results = False
        self.ble_scan_start_time = 0
        self.last_bt510_report_ms = 0
        self.last_bt510_beacon = None
        self.ble_scanner = None
        self.is_scanning_ble = False
        self.btn0_state = 1
        self.btn1_state = 1
        self.http_server = None
        self.mqtt_keepalive_seconds = 60
        self.mqtt_ping_interval_ms = 30000
        self.mqtt_ping_time_counter = 0
        self.last_bt510_beacon_publish_ms = 0
        self.http_listen_port = 80
        self.led0 = Pin('LED0', Pin.OUT, Pin.PULL_NONE)
        self.led1 = Pin('LED1', Pin.OUT, Pin.PULL_NONE)
        self.btn0 = Pin('BUTTON0', Pin.IN, Pin.PULL_NONE)
        self.btn1 = Pin('BUTTON1', Pin.IN, Pin.PULL_UP)
        self.i2c = None
        self.led0.off()
        self.led1.off()
        self.error_state = False
        self.config_mode_timer = None
        self.enter_configuration_mode = False

    def button_pressed(self):
        # Check if the button is pressed
        if self.btn0.value() == 0:
            return True
        else:
            return False

    def config_mode_timer_cb(self, data):
        self.led0.toggle()
        if self.error_state:
            self.led1.toggle()

    def board_init(self):
        self.btn0.configure_event(self.button0_handler, Pin.EVENT_BOTH)
        self.btn1.configure_event(self.button1_handler, Pin.EVENT_BOTH)
        self.i2c = I2C(("I2C0","SDA","SCL"),0x41)
        self.th4click = TempHum4Click(self.i2c)
        if self.th4click.is_present():
            self.th4click.configure()
        else:
            self.th4click = None

    def byte_to_signed_int8(self, byte_value):
        if byte_value > 127:
            return byte_value - 256
        else:
            return byte_value

    def truncate_string(self, s, max_length):
        if len(s) <= max_length:
            return s
        else:
            return s[:max_length - 3] + "..."

    def ble_scan_complete(self):
        if self.enter_configuration_mode:
            pass
        else:
            self.new_ble_scan_results = True

    def scan_results_has_address(self, addr):
        for tup in self.ble_scan_result_list:
            if tup.addr == addr:
                return True
            else:
                return False

    # If valid Canvas BT510 beacon, return a dictionary otherwise return None
    def get_canvas_bt510_beacon(self, ad_tuple):
        i = 0
        beacon = {}
        data = ad_tuple.data
        while i < len(data):
            element_len = data[i]
            if element_len == 0 or element_len > len(data) - i - 1:
                return None
            element_type = data[i + 1]
            if element_len > 1:
                element_data = data[i + 2 : i + element_len + 1]
                #print(element_len,'bytes type',element_type,'data:',element_data)
                if element_type == 0x09:
                    beacon['name'] = element_data.decode('utf-8')
                if element_type == 0xFF:
                    if element_data[0] == 0x77:
                        if element_data[2] == 0xc9:
                            beacon['rssi'] = ad_tuple.rssi
                            beacon['type'] = element_data[1]
                            beacon['fwd'] = 'bt5-' + canvas_ble.addr_to_str(ad_tuple.addr)[2:].lower()
                            beacon['accel_x'] = self.byte_to_signed_int8(element_data[5] | (element_data[4] << 8))
                            beacon['accel_y'] = self.byte_to_signed_int8(element_data[7] | (element_data[6] << 8))
                            beacon['accel_z'] = self.byte_to_signed_int8(element_data[9] | (element_data[8] << 8))
                            beacon['counter'] = element_data[10]
                            beacon['flags'] = element_data[11]
                            beacon['temperature'] = (175.72*(element_data[13] | (element_data[12] << 8))/65536.0) - 46.85
                            beacon['battery'] = element_data[15] | (element_data[14] << 8)
                            return beacon
            i += 1 + element_len
        return None

    def ble_scan_result_canvas_bt510_cb(self, e):
        beacon = self.get_canvas_bt510_beacon(e)
        if beacon is not None:
            if (time.ticks_ms() - self.last_bt510_report_ms) > 5000:
                self.is_scanning_ble = False
                self.ble_scanner.stop()
                self.last_bt510_report_ms = time.ticks_ms()
                self.last_bt510_beacon = beacon

    def ble_scan_result_any_cb(self, e):
        if not self.scan_results_has_address(e.addr):
            self.ble_scan_result_list.append(e)
            if len(self.ble_scan_result_list) >= 10 or (time.ticks_ms() - self.ble_scan_start_time) > self.config['ble_scan_timeout_ms']:
                self.is_scanning_ble = False
                self.ble_scanner.stop()
                self.ble_scan_complete()

    def ble_init(self):
        canvas_ble.init()
        if self.config['gateway_canvas_bt510']:
            self.ble_scanner = canvas_ble.Scanner(self.ble_scan_result_canvas_bt510_cb)
        else:
            self.ble_scanner = canvas_ble.Scanner(self.ble_scan_result_any_cb)

    def start_ble_scan(self):
        self.ble_scan_start_time = time.ticks_ms()
        self.ble_scan_result_list.clear()
        if self.is_scanning_ble == False:
            self.ble_scanner.start(1)
            self.is_scanning_ble = True

    def get_ble_scan_list_html(self):
        html = '<table><tr><th>Address</th><th>RSSI</th><th>Data</th></tr>'
        for entry in self.ble_scan_result_list:
            html += "<tr><td>" + binascii.hexlify(entry.addr).decode()[2:] + "</td><td>" + str(entry.rssi) + "</td><td>" + self.truncate_string(binascii.hexlify(entry.data).decode(), 40) + "</tr>"
        html += "</table>"
        return html

    def connect_station(self, retries):
        for retries in range(retries):
            if(retries > 0):
                print('Connection failed, retrying...')
            self.sta.connect(self.config['sta_ssid'], self.config['sta_passphrase'])
            if self.sta.is_connected():
                self.led0.on()
                return True
            else:
                self.led0.off()
                time.sleep(1)
        
        print('Connection failed, entering configuration mode')
        return False

    def create_response_header(self, content_type, content_len):
        return 'HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\nCache-Control: no-cache,no-store\r\n\r\n' % (content_type, content_len)

    def get_ok_response(self):
        msg = '{"status":"ok"}'
        html = self.create_response_header('application/json', len(msg)) + msg
        return html

    def post_message_response(self, msg):
        msg = '{"status":"ok", "message":"' + msg + '"}'
        html = self.create_response_header('application/json', len(msg)) + msg
        return html

    def get_ssid_scan_list(self, server, conn, headers, body):
        # Send a response containing a JSON object containing the network list
        scan_list = '{"networks":['
        for idx, n in enumerate(self.network_list):
            scan_list += '{"ssid":"' + n[0] + '","rssi":' + str(n[3]) + '}'
            if idx < len(self.network_list) - 1:
                scan_list += ','
        scan_list += ']}'
        server.send_chunked(conn, self.create_response_header('application/json', len(scan_list)) + scan_list)
        return False

    def get_ble_scan_list(self, server, conn, headers, body):
        # Send an HTML response containing the BLE scan result list
        html = self.get_ble_scan_list_html()
        server.send_chunked(conn, self.create_response_header('text/html', len(html)) + html)
        return False

    def get_fwinfo_handler(self, server, conn, headers, body):
        un = os.uname()
        data = '{"machine":"' + un.machine + '","release":"' + un.release + '","mpver":"' + un.version + '","compat":"' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2]) + '","app_id":"' + App.app_id + '","app_ver":"' + App.app_ver + '"}'
        server.send_chunked(conn, self.create_response_header('application/json', len(data)) + data)
        return False

    def get_status_handler(self, server, conn, headers, body):
        # Send a response containing the status of the buttons and LEDs
        # If on the demo page, don't blink LED0
        if self.config_mode_timer.is_running():
            self.config_mode_timer.stop()

        state = '{"btn0":' + str(self.btn0.value() is 0).lower() + ',' + \
                '"btn1":' + str(self.btn1.value() is 0).lower() + ',' + \
                '"led0":' + str(self.led0.value() is 1).lower() + ',' + \
                '"led1":' + str(self.led1.value() is 1).lower() + '}'
        server.send_chunked(conn, self.create_response_header('application/json', len(state)) + state)
        return False

    def get_config_handler(self, server, conn, headers, body):
        # Send the configuration dictionary contents as a string
        config_json = json.dumps(self.config)
        html = self.create_response_header('application/json', len(config_json)) + config_json
        server.send_chunked(conn, html)
        return False

    def post_wifi_save_handler(self, server, conn, headers, body):
        params = {}
        for param in body.split('\r\n')[-1].split('&'):
            params[param.split('=')[0]] = param.split('=')[1]
        # Get the SSID and passphrase from the request
        self.config['sta_ssid'] = HttpServer.url_parse(params['sta_ssid'])
        self.config['sta_passphrase'] = HttpServer.url_parse(params['sta_passphrase'])
        # Send a response
        server.send_chunked(conn, self.get_ok_response())
        self.save_config()
        return False

    def post_webhook_save_handler(self, server, conn, headers, body):
        params = {}
        for param in body.split('\r\n')[-1].split('&'):
            params[param.split('=')[0]] = param.split('=')[1]
        # Get the WebHook URL from the request
        self.config['webhook_url'] = HttpServer.url_parse(params['webhook_url'])
        # Send a response
        server.send_chunked(conn, self.get_ok_response())
        self.save_config()
        return False

    def post_mqtt_save_handler(self, server, conn, headers, body):
        params = {}
        for param in body.split('\r\n')[-1].split('&'):
            params[param.split('=')[0]] = param.split('=')[1]
        # Get the MQTT configuration from the request
        self.config['mqtt_client_id'] = HttpServer.url_parse(params['mqtt_client_id'])
        self.config['mqtt_hostname'] = HttpServer.url_parse(params['mqtt_hostname'])
        self.config['mqtt_port'] = int(HttpServer.url_parse(params['mqtt_port']))
        self.config['mqtt_username'] = HttpServer.url_parse(params['mqtt_username'])
        self.config['mqtt_password'] = HttpServer.url_parse(params['mqtt_password'])
        self.config['mqtt_telemetry_publish_topic'] = HttpServer.url_parse(params['mqtt_telemetry_publish_topic'])
        self.config['mqtt_rpc_request_topic'] = HttpServer.url_parse(params['mqtt_rpc_request_topic'])
        self.config['mqtt_rpc_response_topic'] = HttpServer.url_parse(params['mqtt_rpc_response_topic'])
        # Send a response
        server.send_chunked(conn, self.get_ok_response())
        self.save_config()
        return False

    def post_rpc_handler(self, server, conn, headers, body):
        #print('headers:', headers)
        params = {}
        for param in body.split('\r\n')[-1].split('&'):
            params[param.split('=')[0]] = param.split('=')[1]
        # Get the command and parameter from the request
        if 'toggle_led' in params:
            idx = HttpServer.url_parse(params['toggle_led'])
            if idx == '0':
                self.led0.toggle()
            elif idx == '1':
                self.led1.toggle()
            server.send_chunked(conn, self.get_ok_response())
            return False
        elif 'ble_scan_start' in params:
            self.config['ble_scan_timeout_ms'] = int(HttpServer.url_parse(params['ble_scan_start']))
            server.send_chunked(conn, self.get_ok_response())
            self.start_ble_scan()
            return False
        elif 'cmd' in params:
            cmd = HttpServer.url_parse(params['cmd'])
            if cmd == 'reboot':
                print('Rebooting...')
                server.send_chunked(conn, self.post_message_response('Rebooting...'))
                machine.reset()
                # NOTE: won't get here
                return False
            elif cmd == 'clearwifi':
                print('Clearing Wi-Fi credentials...')
                try:
                    self.config['sta_ssid'] = ''
                    self.config['sta_passphrase'] = ''
                    self.save_config()
                except:
                    pass
                server.send_chunked(conn, self.post_message_response('Wi-Fi credentials cleared'))
                return False
        
        server.send_chunked(conn, self.get_ok_response())
        return False

    def post_connect_handler(self, server, conn, headers, body):
        # Send a response
        server.send_chunked(conn, self.get_ok_response())
        # Returning 'True' here will stop the HTTP server
        return True

    def load_config(self):
        # Load configuration from a file
        f = None
        try:
            f = open('config.txt', 'r')
        except:
            pass
        if f:
            self.config = json.loads(f.read())
            f.close()
        else:
            # Set default config values
            device_id = binascii.hexlify(self.sta.get_mac()).decode()
            self.config['sta_ssid'] = ''
            self.config['sta_passphrase'] = ''
            self.config['ap_ssid'] = 'Veda-' + device_id[-4:]
            self.config['ap_passphrase'] = 'testingwifi123'
            self.config['mqtt_client_id'] = device_id
            self.config['mqtt_hostname'] = 'mqtt.thingsboard.cloud'
            self.config['mqtt_port'] = 1883
            self.config['mqtt_username'] = ''
            self.config['mqtt_password'] = ''
            self.config['mqtt_telemetry_publish_topic'] = 'v1/devices/me/telemetry'
            self.config['mqtt_rpc_request_topic'] = 'v1/devices/me/rpc/request/+'
            self.config['mqtt_rpc_response_topic'] = 'v1/devices/me/rpc/response'
            self.config['ble_scan_timeout_ms'] = 3000
            self.config['sta_connection_retry_count'] = 3
            self.config['gateway_canvas_bt510'] = False
            self.config['webhook_url'] = ''
            print('No config file found, using default values')

    def scan_for_networks(self):
        self.network_list = []
        # Perform 3 scans to get a broader list of networks
        for i in range(3):
            sr = self.sta.scan()
            if sr is not None:
                for n in sr:
                    found = False
                    for m in self.network_list:
                        if n[0] == m[0]:
                            found = True
                            break
                    if not found:
                        self.network_list.append(n)
        pass

    def connect_if_configured(self):
        if self.config['sta_ssid'] != '' and self.config['sta_passphrase'] != '':
            # Connect to the network
            if self.connect_station(self.config['sta_connection_retry_count']):
                # Connection successful, do not enter configuration mode
                self.enter_configuration_mode = False
                return True
        else:
            print('Saved ssid/passphrase not found, entering configuration mode')
            self.enter_configuration_mode = True
        return False

    def save_config(self):
        # Save configuration to a file
        f = open('config.txt', 'w')
        f.write(json.dumps(self.config))
        f.close()

    # Webhook functions
    def webhook_send(self):
        if self.whook is not None:
            msg = {}
            msg['button0'] = self.btn0.value() is 0
            msg['button1'] = self.btn1.value() is 0
            msg['led0'] = self.led0.value() is 1
            msg['led1'] = self.led1.value() is 1
            self.whook.send_message(json.dumps(msg))

    # MQTT functions
    def publish_ssid(self):
        if self.mqtt is not None:
            data = '{ip:"' + self.sta.get_ip() + '",rssi:' + str(self.sta.get_rssi()) + ',ssid:"' + self.sta.get_ssid() + '",ch:' + str(self.sta.get_channel()) + '}'
            self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], data)

    def publish_version(self):
        if self.mqtt is not None:
            un = os.uname()
            data = '{machine:"' + un.machine + '",release:"' + un.release + '",version:"' + un.version + '",mpver:"' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2]) + '",app_id:"' + App.app_id + '",app_ver:"' + App.app_ver + '"}'
            self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], data)

    def publish_btn_led(self):
        if self.mqtt is not None:
            # Publish a message
            data = '{button0:' + str(self.btn0.value() is 0) + ',button1:' + str(self.btn1.value() is 0) + ',led0:' + str(self.led0.value() is 1) + ',led1:' + str(self.led1.value() is 1) + '}'
            self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], data.lower())

    # publish data from a dictionary on behalf of another device
    def publish_fwd_msg(self, data):
        if self.mqtt is not None:
            self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], json.dumps(data))

    def publish_ble_scan_results(self):
        # Publish the BLE scan results
        if len(self.ble_scan_result_list) == 0:
            return
        scan_results_json = '{bleScanList:"' + self.get_ble_scan_list_html() + '"}'
        self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], scan_results_json)

    def subscribe_message(self):
        # Subscribe to a topic
        self.mqtt.set_callback(self.mqtt_subscribe_cb)
        self.mqtt.subscribe(self.config['mqtt_rpc_request_topic'], 1)

    def start_webhook(self):
        # If webhook_url param is empty, do not create the whook object
        if self.config['webhook_url'] != '':
            self.whook = WebHook(self.config['webhook_url'])

    def reconnect_mqtt(self):
        # Reconnect the MQTT client
        if self.mqtt is not None:
            if self.mqtt.sock is not None:
                self.mqtt.disconnect()
            self.mqtt.connect()
            self.publish_ssid()
            self.publish_version()
            self.publish_btn_led()
            self.subscribe_message()

    def start_mqtt(self):
        # If the username/access token is not set, do not connect
        if self.config['mqtt_username'] == "":
            return

        # Connect the MQTT client
        self.mqtt = MQTTClient(
            self.config['mqtt_client_id'],
            self.config['mqtt_hostname'],
            port=self.config['mqtt_port'],
            user=self.config['mqtt_username'],
            password=self.config['mqtt_password'],
            keepalive=self.mqtt_keepalive_seconds)
        
        self.reconnect_mqtt()

    def stop_mqtt(self):
        # Disconnect the MQTT client
        if self.mqtt is not None:
            self.mqtt.disconnect()

    def mqtt_subscribe_cb(self, topic, msg):
        if self.mqtt is not None:
            # Handle an RPC request
            if topic.startswith(self.config['mqtt_rpc_request_topic'][0:-1]):
                # Parse the message
                if(msg.startswith(b'{"method":"setLed0","params":')):
                    if msg.split(b':')[-1][0:-1] == b'true':
                        self.led0.value(1)
                    elif msg.split(b':')[-1][0:-1] == b'false':
                        self.led0.value(0)
                    self.publish_btn_led()
                if(msg.startswith(b'{"method":"setLed1","params":')):
                    if msg.split(b':')[-1][0:-1] == b'true':
                        self.led1.value(1)
                    elif msg.split(b':')[-1][0:-1] == b'false':
                        self.led1.value(0)
                    self.publish_btn_led()
                if(msg.startswith(b'{"method":"startBleScan"')):
                    self.do_ble_scan = True
                # Send a response                
                self.mqtt.publish(self.config['mqtt_rpc_response_topic'] + '/' + topic.decode().split('/')[-1], msg)

    def mqtt_do_ping(self):
        if self.mqtt is not None:
            self.mqtt.ping()
            self.mqtt_ping_time_counter = time.ticks_ms()
            # Send IP address and RSSI data
            # Send temperature and humidity data if TempHum4Click is connected
            if self.th4click is not None:
                read_data = self.th4click.read()
                data = '{temperature:' + str(read_data['temperature']) + ',humidity:' + str(read_data['humidity']) + '}'
                print('Publishing telemetry data:', data)
                self.mqtt.publish(self.config['mqtt_telemetry_publish_topic'], data)

    def button0_handler(self, v):
        # Toggle LED0 if button0 is pressed
        if self.btn0.value() == 0:
            self.led0.toggle()
        if self.btn0_state != self.btn0.value():
            self.btn0_state = self.btn0.value()
            if self.mqtt is not None:
                self.publish_btn_led()
            self.webhook_send()

    def button1_handler(self, v):
        # Toggle LED1 if button1 is pressed
        if self.btn1.value() == 0:
            self.led1.toggle()
        if self.btn1_state != self.btn1.value():
            self.btn1_state = self.btn1.value()
            if self.mqtt is not None:
                self.publish_btn_led()
            self.webhook_send()
    
    def print_configuration_state(self):
        default_not_configured = 'Not Configured'
        if self.config['sta_ssid'] != '' and self.config['sta_passphrase'] != '':
            print(App.fmt_green + ('{:^30}').format('Wi-Fi: Configured') + App.fmt_stop)
        else:
            print(App.fmt_dark + ('{:^30}').format('Wi-Fi: ' + default_not_configured) + App.fmt_stop)
        
        mqtt_is_configured = default_not_configured
        if self.config['mqtt_username'] == "" or self.config['mqtt_hostname'] == "" or self.config['mqtt_port'] == 0 or self.config['mqtt_telemetry_publish_topic'] == "" or self.config['mqtt_rpc_request_topic'] == "":
            print(App.fmt_dark + ('{:^30}').format('MQTT: ' + default_not_configured) + App.fmt_stop)
        else:
            print(App.fmt_green + ('{:^30}').format('MQTT: Configured') + App.fmt_stop)
        webhook_is_configured = default_not_configured
        if self.config['webhook_url'] != '':
            print(App.fmt_green + ('{:^30}').format('Webhook: Configured') + App.fmt_stop)
        else:
            print(App.fmt_dark + ('{:^30}').format('Webhook: ' + default_not_configured) + App.fmt_stop)

    def start(self, config_mode=False):
        # Initialize the board I/O
        self.board_init()
        # Create the LED blink timer
        self.config_mode_timer = canvas.Timer(500, True, self.config_mode_timer_cb, None)
        # Check if the button is pressed
        self.enter_configuration_mode = config_mode
        if self.enter_configuration_mode:
            self.led0.on()
        # Create the AP interface
        self.ap = Ap()
        # Create the STA interface
        self.sta = Station()
        # Load the config from a file if it exists
        self.load_config()
        # Initialize BLE
        self.ble_init()
        # Print the current configuration state
        self.print_configuration_state()

        # If button was not held on startup and already configured
        # and able to connect, don't enter configuration mode
        if not self.enter_configuration_mode:
            self.connect_if_configured()

        if self.enter_configuration_mode:
            self.led0.on()
            self.config_mode_timer.start()
            try:
                while True:
                    # Enable the LED blink timer if not running
                    if self.config_mode_timer.is_running():
                        self.config_mode_timer.start()
                    # Scan for Wi-Fi networks
                    self.scan_for_networks()
                    # Start the AP network
                    #print('Starting AP with ssid "' + App.fmt_cyan + self.config['ap_ssid'] + App.fmt_stop + '" and passphrase "' + App.fmt_cyan + self.config['ap_passphrase'] + + App.fmt_stop)
                    self.ap.start(self.config['ap_ssid'], self.config['ap_passphrase'])
                    print('AP started\nConnect to the "' + App.fmt_cyan + self.config['ap_ssid'] + App.fmt_stop + '" network and open "' + App.fmt_cyan + 'http://' + self.ap.get_ip() + App.fmt_stop + '" in a browser to continue')
                    # Start the HTTP server
                    self.http_server = HttpServer(self.config)
                    self.http_server.register_get_handler('/config', self.get_config_handler)
                    self.http_server.register_get_handler('/fwinfo', self.get_fwinfo_handler)
                    self.http_server.register_get_handler('/ssid_scan', self.get_ssid_scan_list)
                    self.http_server.register_get_handler('/ble_scan_list', self.get_ble_scan_list)
                    self.http_server.register_post_handler('/wifi_save', self.post_wifi_save_handler)
                    self.http_server.register_post_handler('/connect', self.post_connect_handler)
                    self.http_server.register_post_handler('/webhook_save', self.post_webhook_save_handler)
                    self.http_server.register_post_handler('/mqtt_save', self.post_mqtt_save_handler)
                    self.http_server.register_get_handler('/demo1_status', self.get_status_handler)
                    self.http_server.register_post_handler('/demo1_rpc', self.post_rpc_handler)
                    self.http_server.start_sync(self.ap.get_ip(), self.http_listen_port)
                    print('HTTP server stopped')
                    self.http_server = None
                    gc.collect()

                    # SSID and Passphrase have been provided via POST to the '/connect' endpoint
                    self.config_mode_timer.stop()
                    self.led0.off()
                    time.sleep(2)
                    # Shutdown the AP
                    print('Stopping AP')
                    self.ap.stop()
                    time.sleep(2)
                    # Connect to the network on the STA interface
                    print('Connecting to network ' + self.config['sta_ssid'] + '...')
                    if self.connect_station(self.config['sta_connection_retry_count']):
                        self.save_config()
                        break
                    else:
                        print('Failed to connect to network with retry attempts, rebooting...')
                        machine.reset()
                    
            except Exception as e:
                sys.print_exception(e)

        if not self.sta.is_connected():
            print('Failed to connect to network with retry attempts, rebooting...')
            machine.reset()

        self.enter_configuration_mode = False
        self.start_webhook()
        try:
            self.start_mqtt()
        except MQTTException as e:
            print('Failed to connect to MQTT broker, please check your configuration')
            self.error_state = True
            self.led0.off()
            self.led1.off()
            self.config_mode_timer.start()
            # Loop forever in this state, operater needs to restart in configuration mode
            while True:
                time.sleep(1)
        print('Connected to network ' + App.fmt_cyan + self.config['sta_ssid'] + App.fmt_stop)
        
        # Force BLE to scan for 3 seconds to reduce wait time for MQTT publishing
        self.config['ble_scan_timeout_ms'] = 3000
        if self.mqtt is not None:
            print('Starting MQTT client')
            self.mqtt_do_ping()
            print(App.fmt_green + '{:^80}'.format('MQTT client connected') + App.fmt_stop)
        
        if self.config['gateway_canvas_bt510']:
            # Start scanning for Canvas BT510 beacons
            print('Starting BLE scan for Canvas BT510 beacons')
            self.ble_scanner.start(1)
            self.is_scanning_ble = True

        while True:
            if self.mqtt is not None:
                # Check for new MQTT messages
                try:
                    #print('Waiting for MQTT messages...')
                    self.mqtt.wait_msg()
                except OSError as e:
                    # if keyboard exception is raised, just break out of the loop
                    if 'KeyboardInterrupt' in str(e):
                        break
                    print('OSError, reconnecting...')
                    self.reconnect_mqtt()
                except TimeoutException as e:
                    if 'KeyboardInterrupt' in str(e):
                        break
                    # a timeout exception will be raised when no messages are received
                    pass
                except Exception as e:
                    if 'KeyboardInterrupt' in str(e):
                        break
                    print('Exception from mqtt.wait_msg(), reconnecting...')
                    sys.print_exception(e)
                    self.reconnect_mqtt()
                gc.collect()
            
                # Ping the MQTT server to keep the connection alive
                if time.ticks_diff(time.ticks_ms(), self.mqtt_ping_time_counter) > self.mqtt_ping_interval_ms:
                    try:
                        self.mqtt_do_ping()
                    except Exception as e:
                        sys.print_exception(e)
                        # if keyboard exception is raised, just break out of the loop
                        if 'KeyboardInterrupt' in str(e):
                            break
                        print('MQTT ping failed, reconnecting...')
                        self.reconnect_mqtt()
                    finally:
                        gc.collect()
            
                if self.new_ble_scan_results:
                    gc.collect()
                    try:
                        self.publish_ble_scan_results()
                    except Exception as e:
                        if 'KeyboardInterrupt' in str(e):
                            break
                        self.reconnect_mqtt()
                    self.new_ble_scan_results = False
            else:
                # if MQTT is not configured, just sleep for a bit
                time.sleep(1)
            
            if self.config['gateway_canvas_bt510']:
                if (time.ticks_ms() - self.last_bt510_beacon_publish_ms) > 5000:
                    if self.is_scanning_ble == False:
                        self.ble_scanner.start(1)
                        self.is_scanning_ble = True
                    if self.last_bt510_beacon != None:
                        self.last_bt510_beacon_publish_ms = time.ticks_ms()
                        self.publish_fwd_msg(self.last_bt510_beacon)
                        self.last_bt510_beacon = None

            # Check if BLE scan should be started
            if self.do_ble_scan:
                try:
                    gc.collect()
                    self.start_ble_scan()
                except Exception as e:
                    sys.print_exception(e)
                    break
                self.do_ble_scan = False

        print('Exiting main loop, stopping MQTT client...')
        self.stop_mqtt()
        # Nothing left to do, just reboot and re-connect if configured
        machine.reset()
