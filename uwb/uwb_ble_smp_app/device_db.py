#
# Device Database:
#
# This module maintains a database of devices that are participating in the current
# use case. The database is loaded from a file at startup, and saved to a file
# when modified. The file is stored in CBOR format and only contains the static
# portion of the database. The dynamic portion is maintained in memory only.
#
# Static portion:
#     Device ID: 8 byte hex string
#     Network ID: integer (0-65535)
#     Role: integer (0 = tag/mobile, 1 = anchor/fixed)
#     RSSI Threshold: integer (-128 to 127)
#
# Dynamic portion:
#     BLE Address: bytes
#     Advertisement flags: integer (16 bits)
#     RSSI: integer (-128 to 127)
#     Ranging status: integer (0 = not ranging, 1 = ranging)
#     Connection: Handle to BLE connection object
#     UWB roles: current UWB roles supported by the device
#     Channel mask: current UWB channels supported by the device
#

import util
import config
import ble_ad_flags
import uwb_ble_connect
import uwb_smp_client
import uwb_manager
import zcbor
import PikaStdLib

# Device dictionary
devices = { }

class Device:
    def __init__(self, device_id, network):
        self.network = network
        self.device_id = device_id
        self.role = config.DEV_ROLE_TAG
        self.rssi_threshold = -127
        self.ad_flags = 0
        self.ble_addr = None
        self.rssi = -127
        self.ranging_status = 0
        self.connection = None
        self.uwb_roles_supported = None
        self.uwb_role_selected = None
        self.channel_mask_supported = None
        self.uwb_session = None
        self.uwb_session_id = None

    def ad_update(self, ble_addr, flags, rssi):
        self.ble_addr = ble_addr
        self.ad_flags = flags
        self.rssi = rssi

        # Convert device role
        if (self.ad_flags & ble_ad_flags.ROLE_MASK) == ble_ad_flags.ROLE_ANCHOR:
            self.role = config.DEV_ROLE_ANCHOR
        else:
            self.role = config.DEV_ROLE_TAG

    def should_connect(self):
        # Don't connect to unconfigured devices
        if self.ad_flags & ble_ad_flags.CONFIGURED == 0:
            return False

        # Never connect less than RSSI threshold
        if self.rssi < self.rssi_threshold:
            return False

        # Don't connect if already connected
        if self.connection is not None:
            return False

        # Check roles
        if config.connect_role_match(self.role) is False:
            return False

        # If the device is only a BLE advertiser, always connect
        if self.ad_flags & ble_ad_flags.BLE_SCANNER_MASK == ble_ad_flags.BLE_ADVERTISER:
            return True

        # If the device is also a BLE scanner, we only connect if
        # the other device has a lower device ID than ours
        else:
            if util.device_id_compare(self.device_id, config.device_id_str()) < 0:
                return True

        return False

    def connected(self, conn: uwb_ble_connect.Connection):
        self.connection = conn
        print("Current 2", PikaStdLib.MemChecker.getNow(), conn)
        print("DB connected")
        if conn.is_incoming() is False:
            # Start an SMP client and send the first request
            print("DB starting SMP client")
            self.smp_client = uwb_smp_client.SMPClient(self, conn)
            pass

    def disconnected(self):
        self.connection = None
        self.smp_client = None

    def short_addr(self) -> int:
        # Last two bytes of device ID converted into an integer
        return int(self.device_id[-4:-2],16) << 8 | int(self.device_id[-2:],16)

    def update_smp_info(self, uwb_roles:int, channel_mask:int, session_id:int):
        # Save the information
        self.uwb_roles_supported = uwb_roles
        self.channel_mask_supported = channel_mask

        # Select the UWB role for the device
        if self.uwb_roles_supported == config.UWB_ROLE_RESPONDER:
            self.uwb_role_selected = config.UWB_ROLE_RESPONDER
        elif self.uwb_roles_supported == config.UWB_ROLE_INITIATOR:
            self.uwb_role_selected = config.UWB_ROLE_INITIATOR
        elif self.uwb_roles_supported == config.UWB_ROLE_BOTH:
            self.uwb_role_selected = config.UWB_ROLE_RESPONDER
        else:
            # Invalid role, close the connection
            self.connection.disconnect()

        # Create a UWB session
        self.uwb_session_id = session_id
        if self.uwb_session_id is None:
            self.uwb_session_id = uwb_manager.next_session_id()
        self.uwb_session = uwb_manager.Session(self, self.uwb_role_selected,
            self.uwb_session_id)

    def get_session_info(self):
        return (self.uwb_session_id, self.uwb_role_selected)

    def end_session(self):
        self.uwb_session = None
        self.uwb_session_id = None

def lookup(network, device_id):
    global devices
    if device_id in devices:
        dev = devices[device_id]
        if dev.network == network:
            return devices[device_id]
    return None

def lookup_by_device_id(device_id):
    global devices
    if device_id in devices:
        return devices[device_id]
    return None

def load():
    global devices

    # Load the device database
    print("Loading device database")
    try:
        f = open("device.cb", "rb")
    except:
        print("Device database not found")
        return

    # Read the entire file
    cbor = f.read()
    f.close()
    if cbor is None:
        print("Device database is empty")
        return

    # Convert CBOR to an object (an array, in this case)
    d_array = zcbor.to_obj(cbor)
    if d_array is None:
        print("Device database is corrupt")
        return

    # Create device objects
    for dev in d_array:
        device_id = dev['device_id']
        obj = Device(device_id, dev['network'])
        devices[device_id] = obj
        obj.role = dev['role']
        obj.rssi_threshold = dev['rssi_threshold']

    print("Loaded", len(devices), "devices")

def save():
    global devices

    # Convert the device objects into an array
    d_array = [ ]
    for dev_id in devices:
        dev_obj = { }
        dev = devices[dev_id]
        dev_obj['device_id'] = dev.device_id
        dev_obj['network'] = dev.network
        dev_obj['role'] = dev.role
        dev_obj['rssi_threshold'] = dev.rssi_threshold
        d_array.append(dev_obj)

    # Convert the array back into CBOR
    cbor = zcbor.from_obj(d_array, 0)

    # Write to the file
    f = open("device.cb", "wb")
    size = f.write(cbor)
    f.close()

def reset():
    global devices
    devices = { }
    save()
