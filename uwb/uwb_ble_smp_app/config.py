#
# Device configuration
#
# This module maintains the configuration of the device. The configuration is
# loaded from a file at startup, and saved to a file when modified. The file
# is stored in CBOR format and only contains the static portion of the device
# configuration. The dynamic portion is maintained in memory only.
#
# Static portion:
#    Configured: integer (0 = not configured, 1 = configured)
#    Network ID: integer (0-65535)
#    Role: integer (0 = tag/mobile, 1 = anchor/fixed)
#    BLE Role: integer (0 = scanner, 1 = advertiser, 2 = both)
#    UWB Role: integer (0 = initator, 1 = responder, 2 = both)
#    Mode: integer (0 = tag-to-tag, 1 = tag-to-anchor, 2 = anchor-to-anchor, 3 = any)
#    Range Interval: integer (milliseconds between ranging events)
#    Report bitmask: integer (16-bits)
#    Calculation bitmask: integer (16-bits)
#
# Dynamic portion:
#    Ranging active: integer (0 = not ranging, 1 = ranging)
#    Has coarse position: integer (0 = no, 1 = yes)
#    Coarse position: integer (room/zone identifier)
#    Has fine position: integer (0 = no, 1 = yes)
#    Fine position: 3-tuple of integers (x, y, z)

import util
import sys_info
import zcbor
import sync

# Constants
DEV_ROLE_TAG = 0
DEV_ROLE_ANCHOR = 1

BLE_ROLE_SCANNER = 0
BLE_ROLE_ADVERTISER = 1
BLE_ROLE_BOTH = 2

UWB_ROLE_INITIATOR = 0
UWB_ROLE_RESPONDER = 1
UWB_ROLE_BOTH = 2

MODE_TAG_TO_TAG = 0
MODE_TAG_TO_ANCHOR = 1
MODE_ANCHOR_TO_ANCHOR = 2
MODE_ANY = 3

# Configuration dictionary
config = { }

def load():
    global config

    # Set sane defaults
    config["network"] = 0
    config["role"] = DEV_ROLE_TAG
    config["ble_role"] = BLE_ROLE_ADVERTISER
    config["uwb_role"] = UWB_ROLE_BOTH
    config["mode"] = MODE_TAG_TO_TAG
    config["range_interval"] = 500
    config["report_bitmask"] = 0
    config["calculation_bitmask"] = 0
    config["configured"] = 0
    config["ranging_active"] = 0
    config["has_coarse_position"] = 0
    config["coarse_position"] = 0
    config["has_fine_position"] = 0
    config["fine_position"] = (0, 0, 0)

    # Load the configure from file
    print("Loading configuration")
    try:
        f = open("config.cb", "rb")
    except:
        print("Configuration file not found")
        return

    # Read the entire file
    cbor = f.read()
    f.close()
    if cbor is None:
        print("Configuration file is empty")
        return

    # Convert CBOR to an object (an array, in this case)
    config_file = zcbor.to_obj(cbor)
    if config_file is None:
        print("Device database is corrupt")
        return

    # Copy the configuration from the file
    for c in config_file:
        config[c] = config_file[c]

def save():
    global config

    # Filter out the dynamic portion of the configuration
    config_file = { }
    config_file['configured'] = config['configured']
    config_file["network"] = config["network"]
    config_file["role"] = config["role"]
    config_file["ble_role"] = config["ble_role"]
    config_file["uwb_role"] = config["uwb_role"]
    config_file["mode"] = config["mode"]
    config_file["range_interval"] = config["range_interval"]
    config_file["report_bitmask"] = config["report_bitmask"]
    config_file["calculation_bitmask"] = config["calculation_bitmask"]

    # Convert the configuration to CBOR
    cbor = zcbor.from_obj(config_file, 0)
    if cbor is None:
        print("Unable to convert configuration to CBOR")
        return

    # Write the CBOR to file
    f = open("config.cb", "wb")
    if f is None:
        print("Unable to open configuration file")
        return

    size = f.write(cbor)
    f.close()

def reset():
    # Empty the file
    f = open("config.cb", "wb")
    if f is not None:
        f.close()

    # Reload the configuration
    load()

def connect_role_match(remote_role: int):
    if config["configured"] == 0:
        return False

    if config["mode"] == MODE_TAG_TO_TAG:
        if config["role"] == DEV_ROLE_TAG and remote_role == DEV_ROLE_TAG:
            return True
        return False
    elif config["mode"] == MODE_TAG_TO_ANCHOR:
        if config["role"] == DEV_ROLE_TAG and remote_role == DEV_ROLE_ANCHOR:
            return True
        elif config["role"] == DEV_ROLE_ANCHOR and remote_role == DEV_ROLE_TAG:
            return True
        return False
    elif config["mode"] == MODE_ANCHOR_TO_ANCHOR:
        if config["role"] == DEV_ROLE_ANCHOR and remote_role == DEV_ROLE_ANCHOR:
            return True
        return False
    else:
        return False

def is_ble_scanner() -> int:
    if config["configured"] == 0:
        return False

    if config["ble_role"] == BLE_ROLE_SCANNER or config["ble_role"] == BLE_ROLE_BOTH:
        return True
    else:
        return False

def is_ble_advertiser() -> int:
    if config["configured"] == 0:
        return True

    if config["ble_role"] == BLE_ROLE_ADVERTISER or config["ble_role"] == BLE_ROLE_BOTH:
        return True
    else:
        return False

def device_id_str() -> str:
    return util.bytes_to_hex(device_id_bytes())

def device_id_bytes() -> bytes:
    return sys_info.get(sys_info.DEVICE_ID)

def short_addr() -> int:
    # Last two bytes of device ID converted into an integer
    str = device_id_str()
    return int(str[-4:-2],16) << 8 | int(str[-2:],16)

def is_configured() -> bool:
    return config["configured"] == 1

def network_id() -> int:
    return config["network"]

def get_uwb_roles() -> int:
    return config["uwb_role"]

def is_uwb_responder() -> bool:
    if config["uwb_role"] == UWB_ROLE_RESPONDER or config["uwb_role"] == UWB_ROLE_BOTH:
        return True
    else:
        return False

def get_ranging_active() -> bool:
    return config["ranging_active"] == 1

def set_ranging_active(active: bool):
    if active:
        config["ranging_active"] = 1
    else:
        config["ranging_active"] = 0
    sync.signal()
