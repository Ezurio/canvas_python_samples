app_id='xbit_sera_ranging_demo'
app_ver='0.1.0'

import canvas
import canvas_ble
import canvas_uwb
import time
import machine
import binascii

# Advertising interval
ADVERTISING_INTERVAL_MIN = 100 # milliseconds
ADVERTISING_INTERVAL_MAX = 150 # milliseconds

# Ranging interval
RANGING_INTERVAL_UNICAST = 500 # milliseconds
RANGING_INTERVAL_MULTICAST = 200 # milliseconds

# How long to wait for a ranging result before giving up
UNICAST_RANGING_TIMEOUT = 20 # ranging intervals
MULTICAST_RANGING_TIMEOUT = 100 # ranging intervals

# Tag detection timeout
TAG_DETECT_TIMEOUT = 10000 # milliseconds

# How long to enable LEDs in unicast mode before tags present
UNICAST_LED_TIMEOUT = 30000 # milliseconds

# Flags to track if tags are present in the network
tags_present = False
tags_last_seen = None
unicast_start_time = 0

# Devices dictionary format:
#  key: full device ID string (8 bytes, 16 characters)
#  value: dictionary with the following fields:
#     session_id: session ID
#     short_addr: short address
#     range: range result
#     count: ranging timeout counter
#     timeout: ranging timeout
devices = {}

# Sessions dictionary format:
#   key: session ID string
#   value: dictionary with the following fields:
#     session: session object
#     mode: session mode (unicast or multicast)
#     devices: array of device short addresses
sessions = {}

# MULTI_NODE_MODE definitions
MODE_UNICAST=b'\x00'
MODE_MULTICAST=b'\x01'

# Globals for BLE objects
advertiser = None
scanner = None
main_led_strip = None

# Global manufacturing-specific advertisement data array
manu_data_hdr = [ ]

# Configuration data
config = { }

def set_leds(color):
    main_led_strip.set(0, color)
    # LED strip has "GRB" color order rather than "RGB"
    c = (color & 0xFF0000) >> 8
    c |= (color & 0x00FF00) << 8
    c |= (color & 0xFF)
    for i in range(1,11):
        main_led_strip.set(i, c)

# Function to update the advertising data
def ad_update(restart:bool):
    global advertiser
    global manu_data_hdr
    global devices
    global config

    # Stop advertising
    if restart:
        advertiser.stop()
    advertiser.clear_buffer(False)

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
    for d in devices:
        obj = devices[d]
        tlv = [ 0x00, 0x04 ]
        tlv += [ obj['short_addr'] >> 8, obj['short_addr'] & 0xff ]
        tlv += [ obj['range'] >> 8, obj['range'] & 0xff ]
        manu_data += tlv

    # Add TLVs to advertisement
    advertiser.add_ltv(0x01, bytes([0x06]), False)
    advertiser.add_tag_string(0x09, config['ble_name'], False)
    advertiser.add_ltv(0xff, bytes(manu_data), False)
    advertiser.add_canvas_data(0, config['network_id'], False)
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
    manu_data_hdr += list(machine.unique_id())
    manu_data_hdr += [0x00, 0x00, 0x00, 0x00]

    advertiser = canvas_ble.Advertiser()
    advertiser.set_properties(True, False, True)
    advertiser.set_interval(ADVERTISING_INTERVAL_MIN, ADVERTISING_INTERVAL_MAX)

def range_cb(ranges):
    global devices
    global config
    global tags_present
    global unicast_start_time

    # Update the LED
    color = config['range_led']
    for r in ranges:
        if r.range == 65535:
            color = config['error_led']
            break
    # Turn off LED if we haven't seen any tags in a while
    if tags_present == False:
        if (time.ticks_ms() - unicast_start_time) > UNICAST_LED_TIMEOUT:
            color = 0
    set_leds(color)

    for r in ranges:
        # Find a matching device in the devices dictionary
        dev_id_str = None
        for d in devices:
            if devices[d]['short_addr'] == r.addr:
                dev_id_str = d
                break

        # If found a matching device, update its range
        if dev_id_str is not None:
            obj = devices[dev_id_str]
            obj['range'] = r.range
            if r.range == 65535:
                # Increment count of missed ranges
                count = obj['count']
                count += 1
                obj['count'] = count

                # If we miss too many ranges, stop the session
                if count > obj['timeout']:
                    print("Ranging timeout for", dev_id_str, "in session", obj['session_id'])
                    device_remove(dev_id_str)
            else:
                obj['count'] = 0

    # Update the advertisement data
    ad_update(False)

    # Turn off LED if we haven't seen any tags in a while
    color = config['base_led']
    if tags_present == False:
        if (time.ticks_ms() - unicast_start_time) > UNICAST_LED_TIMEOUT:
            color = 0
    set_leds(color)

def session_start(dev_id, dev_id_str):
    global tags_present
    global sessions

    # Get our short address
    our_dev_id = machine.unique_id()
    local_addr = (int(our_dev_id[6]) << 8) | int(our_dev_id[7])

    # Get peer short address
    peer_addr = (int(dev_id[6]) << 8) | int(dev_id[7])

    # Configure the mode
    if config['anchor_mode'] == 1:
        if tags_present == True:
            # If we're an anchor with tags present, we want a single session
            role = canvas_uwb.ROLE_RESPONDER
            session_id = peer_addr
            mode = MODE_MULTICAST
            pass
        else:
            # If we're an anchor with no tags present, we want multiple sessions
            # Select our role and session ID
            if local_addr < peer_addr:
                role = canvas_uwb.ROLE_INITIATOR
                session_id = (local_addr << 16) | peer_addr
            else:
                role = canvas_uwb.ROLE_RESPONDER
                session_id = (peer_addr << 16) | local_addr
            mode = MODE_UNICAST
    else:
        # If we're a tag, we want a single session
        role = canvas_uwb.ROLE_INITIATOR
        session_id = local_addr
        mode = MODE_MULTICAST

    session_id_str = str(session_id)

    # Check to see if the session already exists
    if session_id_str in sessions:
        # Add this peer to the multicast list
        if peer_addr not in sessions[session_id_str]['devices']:
            print("Add device", dev_id_str, "to session", session_id_str)

            # Add it to the array
            sessions[session_id_str]['devices'].append(peer_addr)

            # Add it to the session
            sessions[session_id_str]['session'].add_multicast(peer_addr)

            # Add it to the devices dictionary
            if dev_id_str not in devices:
                d = {}
                d['session_id'] = session_id
                d['short_addr'] = peer_addr
                d['range'] = 65535
                d['count'] = 0
                d['timeout'] = MULTICAST_RANGING_TIMEOUT
                devices[dev_id_str] = d

        # Session already exists, don't need to create
        return

    # If ranging is not already active, start up the radio
    if len(sessions) == 0:
        # Initialize the radio
        canvas_uwb.init()

        # Disable the current limiter, assume we're on a big battery
        result = canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))

    if mode == MODE_MULTICAST:
        print("Start multicast session", session_id_str)
    else:
        print("Start unicast session", session_id_str, "with", dev_id_str)

    # Create the session
    session = canvas_uwb.session_new(session_id, role)
    session.set_local_addr(local_addr)
    session.set_peer_addr(peer_addr)
    session.set_callback(range_cb)
    session.set_app_config(0x03, mode)
    if mode == MODE_UNICAST:
        session.set_ranging_interval(RANGING_INTERVAL_UNICAST)
    else:
        session.set_ranging_interval(RANGING_INTERVAL_MULTICAST)

    # Add multicast devices to the session
    if mode == MODE_MULTICAST:
        print("Add device", dev_id_str, "to session", session_id_str)

    # Start the session
    err = session.start()
    if err == False:
        print("Session start failed")
        return

    # Create a new session record
    s = {}
    s['session'] = session
    s['mode'] = mode
    s['devices'] = [ peer_addr ]
    sessions[session_id_str] = s

    # Create a new device record
    d = {}
    d['session_id'] = session_id
    d['short_addr'] = peer_addr
    d['range'] = 65535
    d['count'] = 0
    if mode == MODE_UNICAST:
        d['timeout'] = UNICAST_RANGING_TIMEOUT
    else:
        d['timeout'] = MULTICAST_RANGING_TIMEOUT
    devices[dev_id_str] = d

def session_stop(session_id):
    global sessions
    global devices

    # Ensure that the session ID is an integer
    session_id = int(session_id)

    print("Session stop", session_id)

    # Find the session
    if str(session_id) in sessions:
        obj = sessions[str(session_id)]
        obj['session'].stop()
        obj['session'].close()
        obj['session'] = None
        obj = None
        del sessions[str(session_id)]

    # Remove sessions's devices from the devices dictionary
    to_remove = []
    for d in devices:
        if devices[d]['session_id'] == session_id:
            to_remove.append(d)
    for d in to_remove:
        del devices[d]

def session_stop_mode(mode):
    to_delete = []
    for s in sessions:
        if sessions[s]['mode'] == mode:
            to_delete.append(s)
    for s in to_delete:
        session_stop(s)

def device_remove(dev_id_str):
    global devices
    global sessions

    # Find the device
    if dev_id_str in devices:
        obj = devices[dev_id_str]
        session_id = obj['session_id']
        short_addr = obj['short_addr']
        obj = None
        del devices[dev_id_str]

        # Find the session
        if str(session_id) in sessions:
            obj = sessions[str(session_id)]
            if short_addr in obj['devices']:
                obj['devices'].remove(short_addr)
                if obj['mode'] == MODE_MULTICAST:
                    obj['session'].del_multicast(short_addr)
            length = len(obj['devices'])
            obj = None
            if length == 0:
                session_stop(session_id)

def scan_cb(evt):
    global config
    global tags_present
    global tags_last_seen
    global unicast_start_time

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
    device_id_str = binascii.hexlify(device_id).decode()
    network_id = int(m[4]) << 8 | int(m[5])
    flags = int(m[6])

    # Match network IDs
    if network_id != config['network_id']:
        return

    # Keep track of whether we've seen a tag in the network
    if (flags & 0x02) == 0:
        if tags_present == False:
            print("Tags are present")
            # Stop all anchor (unicast) ranging sessions
            session_stop_mode(MODE_UNICAST)

        tags_last_seen = time.ticks_ms()
        tags_present = True

    # Timeout the tags_present flag if we don't see a tag for a while
    if tags_last_seen is not None:
        if (time.ticks_ms() - tags_last_seen) > TAG_DETECT_TIMEOUT:
            print("Tags are not present")
            tags_present = False
            tags_last_seen = None
            # Stop all tag (multicast) ranging sessions
            session_stop_mode(MODE_MULTICAST)
            unicast_start_time = time.ticks_ms()

    if config['anchor_mode'] == 1:
        # If we're an anchor with tags present, we don't want to range
        # with other anchors
        if tags_present == True:
            if (flags & 0x02) == 0x02:
                return
    else:
        # If we're a tag, we don't want to range with other tags
        if (flags & 0x02) == 0:
            return

    # Start a session if we don't have one already
    if device_id_str not in devices:
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
    for s in list(sessions.keys()):
        obj = sessions[s]
        sess = obj['session']
        sess.stop()
        sess.close()
        obj['session'] = None
        sess = None
        del sessions[s]

def stop():
    scan_stop()
    ad_stop()
    ranging_stop()

def config_load():
    global config
    global tags_present

    config = {}
    config['ble_name'] = "UWB Simple"
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

    config_file = canvas.zcbor_to_obj(cbor)
    if config_file is None:
        config_save()
        return

    for c in config_file:
        config[c] = config_file[c]

    # If we're not an anchor, then tags are present in the network
    if config['anchor_mode'] == 0:
        tags_present = True

def config_save():
    global config

    cbor = canvas.zcbor_from_obj(config, 0)
    if cbor is None:
        return

    f = open("config.cb", "wb")
    if f is None:
        return

    size = f.write(cbor)
    f.close()

def connection_cb(conn):
    pass

def disconnection_cb(conn):
    # restart advertising
    ad_update(True)

# Initialize the LED
main_led_strip = canvas.LEDStrip("", 12)
set_leds(0)

config_load()

print("My device ID is", binascii.hexlify(machine.unique_id()).decode())
unicast_start_time = time.ticks_ms()

# Initialize and start advertising
canvas_ble.init()
canvas_ble.set_periph_callbacks(connection_cb, disconnection_cb)
ad_init()
ad_update(True)

# Initialize and start scanning
scan_init()
scan_start()

set_leds(config['base_led'])
