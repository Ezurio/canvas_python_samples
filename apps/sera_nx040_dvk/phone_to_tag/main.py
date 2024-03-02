import canvas
import canvas_ble
import canvas_uwb
import binascii
import machine
import struct

##############################################################################
# Local variables
##############################################################################

# My address
addr = machine.unique_id()[6] << 8 | machine.unique_id()[7]

# Phone type
ios = False

# BLE Connection status
connection = None
DESIRED_SEC = 2
sec_level = 0
call_ios_init = False

# BLE objects
adv = None
gattserver = None

# UWB objects
session = None

##############################################################################
# Functions
##############################################################################

def range_cb(ranges):
    for r in ranges:
        if r.range != canvas_uwb.RANGE_ERROR:
            print("Range:", r)

def ble_conn_cb(c):
    global connection
    connection = c
    print("BLE connected to", canvas_ble.addr_to_str(c.get_addr()))

    # Try to improve security
    c.set_security_cb(ble_security_cb)
    try:
        c.change_security(DESIRED_SEC)
    except:
        print("Failed to change security")
        c.delete_pairing(True)
        c.change_security(DESIRED_SEC)

def ble_disconn_cb(c):
    global connection
    global session
    global sec_level
    global call_ios_init

    connection = None
    print("BLE disconnected from", canvas_ble.addr_to_str(c.get_addr()))

    # Stop any outstanding UWB session
    if session is not None:
        session.stop()
        session = None
    
    # Reset our security variables
    sec_level = 0
    call_ios_init = False

    # Restart advertising
    adv.start()

def ble_security_cb(c, level):
    global sec_level
    global call_ios_init

    # Save the security level that we got
    print("BLE Connection to {} is at security level {}".format(
        canvas_ble.addr_to_str(c.get_addr()), level))
    sec_level = level

    if level != DESIRED_SEC:
        print("Security level is not high enough")
        c.delete_pairing(False)
    elif call_ios_init:
        # We were waiting for security to be enabled
        initialize_ios()
        call_ios_init = False

def initialize_ios():
    global call_ios_init

    print("Received QPP RX Initialize message for iOS")

    # We can't send our reply to this message until we have enabled
    # the security level we need. Since this is already a callback
    # function, we can't wait here. Instead, we'll just set a flag
    # and let the security callback function call us again.
    if sec_level != DESIRED_SEC:
        print("Wait for security")
        call_ios_init = True
        return

    # Fetch some data
    canvas_uwb.init()
    info = canvas_uwb.get_device_info()

    # Build the response
    data = []
    data += [ 0x01 ] # Initialized Response
    data += [ 0x01, 0x00 ] # Spec version Major
    data += [ 0x00, 0x00 ] # Spec version Minor
    data += [ 20 ] # Preferred update rate
    data += [ 0 ] * 10 # RFU
    data += [ 21 ] # UWBConfigDataLength
    data += [ 0x01, 0x00 ] # UWB spec version major
    data += [ 0x01, 0x00 ] # UWB spec version minor
    data += [ 0x32, 0x11, 0x10, 0x00 ] # Manufacturer ID
    data += [ info.firmware_version[0], 0x02, 0x02, 0x00 ] # Model ID
    data += [ 0x00, 0x00, 0x03, 0x04 ] # Middleware Version
    data += [ 0x01 ] # Ranging role
    data += [ addr >> 8, addr & 0xff ] # Device MAC address
    data += [ 100, 0 ] # Clock drift

    # Update the Nearby data characteristic
    gattserver.write("Nearby Data", bytes(data[1:]))

    # Send the response back to the phone
    gattserver.notify(connection, "QPP TX", bytes(data))

def initialize_android():
    print("Received QPP RX Initialize message for Android")

    # Fetch some data
    canvas_uwb.init()
    info = canvas_uwb.get_device_info()

    # Build the response
    data = [ ]
    data += [ 0x01 ] # Initialized Response
    data += [ 0x01, 0x00 ] # Spec version Major
    data += [ 0x00, 0x00 ] # Spec version Minor
    data += [ 0x00, 0x02 ] # Chip ID - SR040
    data += [ info.firmware_version[0], info.firmware_version[1] ] # Chip FW Version
    data += [ 0x04, 0x03, 0x00 ] # Middleware Version
    data += [ 0x00, 0x00, 0x00, 0x07 ] # Supported profile IDs
    data += [ 0x03 ] # Ranging role
    data += [ addr & 0xff, addr >> 8 ] # Device MAC address
    
    # Send the response back to the phone
    gattserver.notify(connection, "QPP TX", bytes(data))

def configure_ios(data):
    global session
    print("Received iOS Configure message:", binascii.hexlify(data).decode())

    # Create the session
    canvas_uwb.init()
    canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))
    session = canvas_uwb.session_from_profile(canvas_uwb.ROLE_INITIATOR, addr, data)

    # Start the session
    session.set_callback(range_cb)
    session.start()
    print("UWB session started")

    # Clear the Nearby characteristic
    gattserver.write("Nearby Data", bytes(48))

    # Send the response back to the phone
    gattserver.notify(connection, "QPP TX", bytes([2]))

def configure_android(data):
    global session
    print("Received Android Configure message:", binascii.hexlify(data).decode())

    # Unpack the message into a tuple with the following indices:
    #     0 = Major version
    #     1 = Minor version
    #     2 = Session ID
    #     3 = Preamble code
    #     4 = Channel
    #     5 = Profile
    #     6 = Role
    #     7 = Peer MAC address
    msg = struct.unpack(">HHLBBBBH", data)
    print("Unpacked Android Configure message:", msg)

    # Invert the bytes of the peer address
    peer_addr = msg[7] >> 8 | ((msg[7] & 0xff) << 8)

    # Verify profile
    if msg[5] != 1:
        print("Invalid profile in Android Configure message")
        return

    # Determine our role
    if msg[6] == 1:
        role = canvas_uwb.ROLE_INITIATOR
        print("Role is initiator")
    elif msg[6] == 2:
        role = canvas_uwb.ROLE_RESPONDER
        print("Role is responder")
    else:
        print("Invalid role in Android Configure message")
        return

    # Create the session
    canvas_uwb.init()
    canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))
    session = canvas_uwb.session_new(msg[2], role)
    session.set_local_addr(addr)
    session.set_peer_addr(peer_addr)
    session.set_ranging_interval(240)
    session.set_app_config(canvas_uwb.CONFIG_SLOTS_PER_RR, bytes([6]))
    session.set_app_config(canvas_uwb.CONFIG_PREAMBLE_CODE_INDEX, bytes([msg[3]]))
    session.set_channel(msg[4])
    session.set_app_config(39, bytes([0x08, 0x07]))
    session.set_app_config(40, bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]))
    session.set_callback(range_cb)

    # Start the session
    session.start()
    print("UWB session started")

    # Send the response back to the phone
    gattserver.notify(connection, "QPP TX", bytes([2]))

def stop_ranging():
    global session
    print("Received Stop message")

    # Stop the session if it is active
    if session is not None:
        session.stop()
        session = None

    # Send the response back to the phone
    gattserver.notify(connection, "QPP TX", bytes([3]))

def qpp_rx_cb(event):
    global ios

    # Validate the incoming event
    if event.type != canvas_ble.GattServer.EVENT_ATTR_VALUE:
        print("Invalid QPP RX event type:", event.type)
        return
    if len(event.data) == 0:
        print("Received empty QPP RX message")
        return

    if event.data[0] == 10:
        # Received Initialize message
        ios = True
        if len(event.data) == 1:
            ios = True
        else:
            if event.data[1] == 1:
                ios = False
            elif event.data[1] != 2:
                print("Invalid QPP RX Initialize message")
                return

        # Handle the message
        if ios:
            initialize_ios()
        else:
            initialize_android()

    elif event.data[0] == 11:
        # Received Configure message
        if ios:
            configure_ios(event.data[1:])
        else:
            configure_android(event.data[1:])

    elif event.data[0] == 12:
        # Received Stop message
        print("Received QPP RX Stop message")
        stop_ranging()

    else:
        print("Invalid QPP RX message type:", event.data[0])

GATT_TABLE = {
    "Service 1": {
        "Name": "QPPS",
        "UUID": "6E400001-B5A3-F393-E0A9-E50E24DCCA9E",
        "Characteristic 1": {
            "Name": "QPP RX",
            "UUID": "6E400002-B5A3-F393-E0A9-E50E24DCCA9E",
            "Length": 64,
            "Read Encryption": "None",
            "Write Encryption": "None",
            "Capability": "Write",
            "Callback": qpp_rx_cb
        },
        "Characteristic 2": {
            "Name": "QPP TX",
            "UUID": "6E400003-B5A3-F393-E0A9-E50E24DCCA9E",
            "Length": 64,
            "Read Encryption": "None",
            "Write Encryption": "None",
            "Capability": "Notify",
        }
    },
    "Service 2": {
        "Name": "Nearby",
        "UUID": "48fe3e40-0817-4bb2-8633-3073689c2dba",
        "Characteristic 1": {
            "Name": "Nearby Data",
            "UUID": "95e8d9d5-d8ef-4721-9a4e-807375f53328",
            "Length": 48,
            "Read Encryption": "Encrypt",
            "Write Encryption": "None",
            "Capability": "Read",
        }
    }
}

# Initialize BLE and our GATT server
canvas_ble.init()
canvas_ble.set_periph_callbacks(ble_conn_cb, ble_disconn_cb)
gattserver = canvas_ble.GattServer()
gattserver.build_from_dict(GATT_TABLE)
gattserver.start()

# Start advertising
adv = canvas_ble.Advertiser()
adv.clear_buffer(True)
adv.add_canvas_data(0, 0, True)
adv.clear_buffer(False)
adv.add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([6]), False)
# 6e400001-b5a3-f393-e0a9-e50e24dcca9e
adv.add_ltv(canvas_ble.AD_TYPE_UUID128_COMPLETE,
    b'\x9e\xca\xdc\x24\x0e\xe5\xa9\xe0\x93\xf3\xa3\xb5\x01\x00\x40\x6e', False)
adv.add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, "UWB", False)
adv.set_properties(True, True, False)
adv.set_interval(100, 200)
adv.start()
