import canvas
import canvas_ble
import canvas_uwb
import time

# 6818a4f7-31db-4073-b8b4-47f1d798c280
MY_UUID=b'\x80\xc2\x98\xd7\xf1G\xb4\xb8s@\xdb1\xf7\xa4\x18h'

UWB_SESSION_ID=0x12345678
UWB_INITIATOR_ADDR=0x2222
UWB_RESPONDER_ADDR=0x1111
UWB_RANGING_INTERVAL=200
UWB_RANGING_TIMEOUT=10000

led = canvas.LEDStrip("", 1)
led_color = 0x000000
led.set(0, led_color)

advertiser = None
ad_timer = None
session = None
range_timer = None

def ad_timer_cb(data):
    global advertiser
    global ad_timer
    print("Starting advertising")
    try:
        advertiser.start()
    except:
        print("Failed. Try again later")
        advertiser.stop()
        ad_timer.start()

def ble_connected(conn):
    global led_color
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))
    led_color |= 0x00003f
    led.set(0, led_color)

def ble_disconnected(conn):
    global ad_timer
    global led_color
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    led_color &= ~0x0000ff
    led.set(0, led_color)
    ad_timer.start()

def ranging_result(results):
    global led_color
    led_color &= ~0x00ff00
    for result in results:
        if result.range != canvas_uwb.RANGE_ERROR:
            print("Range", result.range)
            led_color |= 0x00ff00
            range_timer.restart()
    led.set(0, led_color)

def start_ranging():
    global session
    print("Starting ranging")
    canvas_uwb.init()
    result = canvas_uwb.raw_uci_send(
        bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))
    session = canvas_uwb.session_new(
        UWB_SESSION_ID, canvas_uwb.ROLE_INITIATOR)
    session.set_local_addr(UWB_INITIATOR_ADDR)
    session.set_peer_addr(UWB_RESPONDER_ADDR)
    session.set_callback(ranging_result)
    session.set_app_config(
        canvas_uwb.CONFIG_MULTI_NODE_MODE, canvas_uwb.MODE_UNICAST)
    session.set_ranging_interval(UWB_RANGING_INTERVAL)
    err = session.start()

def range_timer_cb(data):
    global session
    global led_color
    print("Range timer expired")
    led_color &= ~0x00ff00
    led.set(0, led_color)
    session.stop()
    session.close()
    session = None
    time.sleep(1)
    start_ranging()

def start_advertising():
    global advertiser
    global ad_timer
    print("Starting advertising")
    canvas_ble.init()
    canvas_ble.set_periph_callbacks(ble_connected, ble_disconnected)
    advertiser = canvas_ble.Advertiser()
    advertiser.add_ltv(
        canvas_ble.AD_TYPE_FLAGS, bytes([0x06]), False)
    advertiser.add_ltv(
        canvas_ble.AD_TYPE_UUID128_COMPLETE, MY_UUID, False)
    ad_timer = canvas.Timer(200, False, ad_timer_cb, None)
    ad_timer.start()

range_timer = canvas.Timer(UWB_RANGING_TIMEOUT, False, range_timer_cb, None)
range_timer.start()
start_ranging()
start_advertising()
