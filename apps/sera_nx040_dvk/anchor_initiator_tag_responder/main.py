import binascii
from rgb import RGB
from config import Config
from anchor import Anchor
from tag import Tag
from machine import Pin
from canvas import Timer
import canvas_ble
import time

#
# UWB Anchor Initiator/Tag Responder Demonstration
# Intended for use with the Sera NX040 DVK
#
#

UWB_BLE_FLAG_CONFIGURED = 0x0001
UWB_BLE_FLAG_ANCHOR = 0x0002
UWB_BLE_FLAG_SCANNING_CAPABLE = 0x0004
UWB_BLE_FLAG_RESPONDER_CAPABLE = 0x0008
UWB_BLE_FLAG_SESSION_ACTIVE = 0x0010

anchor = None
tag = None
advertiser = None
ad_header = b"\x77\x00\x0c\x00\x00\x00"
ad_flags = b"\x00\x00"
ad_data = b""

def display_timer_cb(data):
    global tag
    if tag is not None:
        update_ad_data()
        peer_count = len(config.config['session_id_list'])
        json_str = '{' + '"local":"' + local_addr_str + '",'
        for i in range(peer_count):
            peer_id_str = hex(config.config['session_id_list'][i])[6:]
            json_str += '"' + peer_id_str + '":' + str(tag.devices[peer_id_str]['range'])
            if i < peer_count - 1:
                json_str += ','
        json_str += '}'
        print(json_str)

def ble_connect(conn):
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))

def ble_disconnect(conn):
    global advertiser
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    advertiser.start()

def get_timestamp():
    return time.ticks_ms().to_bytes(4, 'little')

def update_ad_data():
    global local_addr_str, advertiser, ad_data

    advertiser.clear_buffer(False)
    advertiser.add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([0x06]), False)
    advertiser.add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, config.config['ble_name'] + '-' + local_addr_str, False)
    advertiser.add_ltv(canvas_ble.AD_TYPE_MANU_SPECIFIC, ad_header + ad_flags + config.config['dev_id'] + get_timestamp() + ad_data, False)

    peer_count = len(config.config['session_id_list'])
    ad_data = b""
    for i in range(peer_count):
        peer_id_str = hex(config.config['session_id_list'][i])[6:]
        ad_data += b"\x00\x04"
        ad_data += binascii.unhexlify(peer_id_str.encode())
        ad_data += tag.devices[peer_id_str]['range'].to_bytes(2, 'little')

    advertiser.update()


def start_app():
    global config, led, anchor, tag, display_timer, local_addr_str, advertiser, ad_header, ad_flags, ad_data
    
    # Display our device ID and resulting short address
    def print_banner():
        print("My Device ID is", binascii.hexlify(config.config['dev_id']).decode(), "( short address ", local_addr_str, ", name: '" + local_name + "')")

    config = Config()  # Create an instance of the Config class to manage configuration
    led = RGB()  # Create an instance of the RGB class to control the RGB LED
    led.set(config.config['base_led'])  # Set the LED color based on the configuration

    local_addr_str = hex(config.config['local_addr'])[2:]
    local_name = config.config['ble_name']

    # If this is an anchor, start the anchor code
    if config.config['anchor_mode'] == 1:
        print('\r\n-------------------------' + ('-' * len(local_name)))
        print('| Anchor Mode |',local_addr_str,'|',local_name,'|')
        print('-------------------------' + ('-' * len(local_name)))
        print_banner()
        print('-' * 120 + '\r\n')
        anchor = Anchor(config, led)
        anchor.start()
    # otherwise start tag code
    elif config.config['anchor_mode'] == 0:
        print('\r\n----------------------' + ('-' * len(local_name)))
        print('| Tag Mode |',local_addr_str,'|',local_name,'|')
        print('----------------------' + ('-' * len(local_name)))
        print_banner()
        print('-' * 120 + '\r\n')
        tag = Tag(config, led)
        tag.start()
        # start a timer to display ranging data 10 times a second
        display_timer = Timer(100, True, display_timer_cb, None)
        display_timer.start()
        # start the BLE advertising
        canvas_ble.init()
        canvas_ble.set_periph_callbacks(ble_connect, ble_disconnect)
        ad_flags = (UWB_BLE_FLAG_CONFIGURED | UWB_BLE_FLAG_RESPONDER_CAPABLE | UWB_BLE_FLAG_SESSION_ACTIVE ).to_bytes(2, 'little')
        advertiser = canvas_ble.Advertiser()
        advertiser.set_properties(True, False, True)
        advertiser.set_interval(config.config['advertising_interval_ms'], config.config['advertising_interval_ms'] + 10)
        update_ad_data()
        advertiser.start()
        print('BLE Advertising started as "' + local_name + '-' + local_addr_str + '"')

def stop():
    global anchor, tag, display_timer
    if anchor is not None:
        anchor.stop()
    if tag is not None:
        tag.stop()
        display_timer.stop()

print("\r\n\r\nStarting Application")

button = Pin('GPIO7',Pin.IN,Pin.PULL_UP)
if(button.value() == 0):
    # Skip the rest of the code and go to REPL prompt
    print('Button pressed, skipping application')
else:
    # Continue with the rest of the code
    start_app()
