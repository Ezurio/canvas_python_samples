import sys_info
import canvas_ble
import pi_uwb
import led_strip
import zcbor

# How long to wait for a ranging result before giving up
RANGING_TIMEOUT_COUNT = 10

# Dictionary of active ranging sessions
sessions = {}

# Globals for BLE objects
advertiser = None
scanner = None
main_led_strip = None

# Calibration variables
CALIBRATION_COUNT = 20
cal_mode = False
cal_counts = 0
cal_range_sum = 0

# Global manufacturing-specific advertisement data array
manu_data_hdr = [ ]

# Configuration data
config = { }

# Convert bytes string into hex string
def bytes_to_hex(buf):
    s=''
    for b in buf:
        s+=hex(int(b))[2:]
    return s

# Function to update the advertising data
def ad_update(restart:bool):
    global advertiser
    global manu_data_hdr
    global sessions
    global config

    # Stop advertising
    if restart:
        advertiser.stop()
    advertiser.clear_buffer(0)

    # Set flags
    flags = 0x01
    if config['anchor_mode'] == 1:
        flags |= 0x02
    manu_data_hdr[6] = flags

    # Set network ID
    manu_data_hdr[4] = config['network_id'] >> 8
    manu_data_hdr[5] = config['network_id'] & 0xff

    # Make a copy of the header to append TLVs to
    manu_data = manu_data_hdr + []

    # Add LED color TLV
    tlv = [ 0x0a, 0x03 ]
    c = config['base_led']
    tlv += [ c >> 16, (c >> 8) & 0xff, c & 0xff ]
    manu_data += tlv

    # Add position TLV
    if config['anchor_mode'] == 1:
        tlv = [ 0x05, 0x0C ]
        v = config['anchor_x']
        tlv += [ (v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff ]
        v = config['anchor_y']
        tlv += [ (v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff ]
        v = config['anchor_z']
        tlv += [ (v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff ]
        manu_data += tlv

    # Add TLVs for range results
    for s in sessions:
        obj = sessions[s]
        tlv = [ 0x00, 0x04 ]
        tlv += [ obj['peer_addr'] >> 8, obj['peer_addr'] & 0xff ]
        tlv += [ obj['range'] >> 8, obj['range'] & 0xff ]
        manu_data += tlv

    # Add TLVs to advertisement
    advertiser.add_ltv(0x01, bytes([0x06]), 0)
    advertiser.add_ltv(0xff, bytes(manu_data), 0)
    if restart:
        advertiser.start()
    else:
        advertiser.update()

def ad_stop():
    advertiser.stop()

def ad_init():
    global advertiser
    global manu_data_hdr

    # Build the fixed portion of the advertisement
    manu_data_hdr = [0x77, 0x00]
    manu_data_hdr += [0x0C, 0x00, 0x00, 0x00, 0x00, 0x00]
    manu_data_hdr += list(sys_info.get(sys_info.DEVICE_ID))
    manu_data_hdr += [0x00, 0x00, 0x00, 0x00]

    advertiser = canvas_ble.Advertiser()
    advertiser.set_properties(1, 0, 1)
    advertiser.set_interval(200, 300)

def range_cb(evt):
    global main_led_strip
    global sessions
    global cal_mode
    global cal_counts
    global cal_range_sum
    global config

    if evt.range == 65535:
        main_led_strip.set(0, config['error_led'])
    else:
        main_led_strip.set(0, config['range_led'])
        if cal_mode:
            cal_range_sum = cal_range_sum + evt.range
            cal_counts = cal_counts + 1
            if cal_counts == CALIBRATION_COUNT:
                cal_mode = False
                cal_done(cal_range_sum / cal_counts)

    dev_id_str = None
    for s in sessions:
        if sessions[s]['peer_addr'] == evt.address:
            dev_id_str = s
            break

    if dev_id_str is not None:
        obj = sessions[dev_id_str]
        obj['range'] = evt.range
        if evt.range == 65535:
            count = obj['count']
            count = count + 1
            obj['count'] = count
            if count > RANGING_TIMEOUT_COUNT:
                print("Session stop", dev_id_str)
                sess = obj['session']
                sess.stop()
                # Make sure that the session object is destroyed
                # Not sure what is necessary
                obj['session'] = None
                sess = None
                sessions.remove(dev_id_str)
        else:
            obj['count'] = 0
        ad_update(False)

    main_led_strip.set(0, config['base_led'])

def session_start(dev_id, dev_id_str):
    global sessions

    # If ranging is not already active, start up the radio
    if len(sessions) == 0:
        pi_uwb.init()
        result = pi_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))

    # Get our short address
    our_dev_id = sys_info.get(sys_info.DEVICE_ID)
    local_addr = (int(our_dev_id[6]) << 8) | int(our_dev_id[7])

    # Get peer short address
    peer_addr = (int(dev_id[6]) << 8) | int(dev_id[7])

    # Select our role and session ID
    if local_addr < peer_addr:
        role = pi_uwb.PI_UWB_ROLE_INITIATOR
        session_id = (local_addr << 16) | peer_addr
    else:
        role = pi_uwb.PI_UWB_ROLE_RESPONDER
        session_id = (peer_addr << 16) | local_addr

    session = pi_uwb.session_new(session_id, role)
    session.set_local_addr(local_addr)
    session.set_peer_addr(peer_addr)
    session.set_callback(range_cb)
    session.set_app_config(0x2c, b'\x01') # Set FiRa hopping mode
    session.set_app_config(0x03, b'\x00') # one-to-one mode
    err = session.start()
    if err == False:
        print("Session start failed")
        return

    print("Session start", dev_id_str)

    # Create a new session record
    s = {}
    s['session'] = session
    s['dev_id'] = dev_id
    s['range'] = 65535
    s['count'] = 0
    s['peer_addr'] = peer_addr

    # Store it in the sessions dictionary
    sessions[dev_id_str] = s

def scan_cb(evt):
    global config

    # Only look at extended advertisements
    if evt.type != 5:
        return

    # Get manufacturer-specific data from the advertisement
    m = canvas_ble.find_ltv(0xff, evt.data)

    # If there's no data, do nothing
    if m is None:
        return

    # Our advertisement is at least this long
    if len(m) < 20:
        return

    # Extract some fields
    device_id = m[8:16]
    device_id_str = bytes_to_hex(device_id)
    network_id = int(m[4]) << 8 | int(m[5])
    flags = int(m[6])

    # Match network IDs
    if network_id != config['network_id']:
        return

    # If we're an anchor, don't connect with other anchors
    if config['anchor_mode'] == 1 and (flags & 0x02) != 0:
        return

    # Start a session if we don't have one already
    if device_id_str not in sessions:
        session_start(device_id, device_id_str)

def scan_init():
    global scanner
    scanner = canvas_ble.Scanner(scan_cb)

    # Scan 80 out of 100 milliseconds
    scanner.set_phys(canvas_ble.PHY_1M)
    scanner.set_timing(100, 80)

    # Filter ads for just our manufacturer ID and protocol ID
    scanner.filter_add(3, bytes([0x77, 0x00, 0x0c, 0x00]))

def scan_start():
    global scanner
    scanner.start(0)

def scan_stop():
    global scanner
    scanner.stop()

def ranging_stop():
    global sessions
    for s in sessions:
        obj = sessions[s]
        sess = obj['session']
        sess.stop()
        obj['session'] = None
        sess = None
        sessions.remove(s)

def stop():
    scan_stop()
    ad_stop()
    ranging_stop()

def cal(actual:int):
    # Reset calibration variables
    global cal_counts
    global cal_mode
    global cal_range_sum
    global cal_actual
    cal_counts = 0
    cal_range_sum = 0
    cal_mode = True
    cal_actual = actual
    print("Calibration starting")

def cal_write(val):
    # Stop ranging sessions
    stop()
    raw_uci = [0x2e, 0x26, 0x00, 0x06, 0x01, 0x02, 0x03, 0x09, val & 0xff, (val >> 8) & 0xff ]
    pi_uwb.init()
    pi_uwb.raw_uci_send(bytes(raw_uci))

def cal_done(avg:int):
    print("Calibration average range", avg)
    speed_of_light = 299702547.0
    cal_unit = 15.65e-12
    d_offset = avg - cal_actual
    t_offset = d_offset / (speed_of_light * 100.0)
    cal_value = int(t_offset / cal_unit)
    if cal_value < 0:
        print("Calibration failed", cal_value)
    else:
        cal_write(cal_value)
        print("Calibration done", cal_value)

def config_load():
    global config

    config = {}
    config['base_led'] = 0x000f00
    config['error_led'] = 0x000000
    config['range_led'] = 0x003f00
    config['network_id'] = 0
    config['anchor_mode'] = 0
    config['anchor_x'] = 0
    config['anchor_y'] = 0
    config['anchor_z'] = 0

    try:
        f = open('config.cb', 'rb')
    except:
        print("Config file not found")
        return

    cbor = f.read()
    f.close()
    if cbor is None:
        return

    config_file = zcbor.to_obj(cbor)
    if config_file is None:
        config_save()
        return

    for c in config_file:
        config[c] = config_file[c]

def config_save():
    global config

    cbor = zcbor.from_obj(config, 0)
    if cbor is None:
        return

    f = open("config.cb", "wb")
    if f is None:
        return

    size = f.write(cbor)
    f.close()

# Initialize the LED
boot_led_strip = None
main_led_strip = led_strip.led_strip("", 1)
main_led_strip.set(0, 0x000000)

config_load()

# Initialize and start advertising
canvas_ble.init()
ad_init()
ad_update(True)

# Initialize and start scanning
scan_init()
scan_start()

main_led_strip.set(0, config['base_led'])
