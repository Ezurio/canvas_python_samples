import device_db
import uwb_ble_connect
import util
import pi_ble_scanner

# Global for the scanner object
scanner = None

# Ignore list (devices we see that aren't in our network or database)
ignore_list = []

def scan_cb(evt):
    # Only look at extended advertisements
    if evt.type != 5:
        return

    # Get manufacturer-specific data from the advertisement
    m = pi_ble_scanner.find_ltv(0xff, evt.data)

    # If there's no data, do nothing
    if m is None:
        return

    # Our advertisement is at least this long
    if len(m) < 20:
        return

    # Extract some fields
    network = int(m[4]) | (int(m[5]) << 8)
    flags = int(m[6]) | (int(m[7]) << 8)
    device_id = util.bytes_to_hex(m[8:16])

    # Find the device in our database
    db = device_db.lookup(network, device_id)
    if db is None:
        if device_id not in ignore_list:
            print("Found device", device_id, "on network", network, "but not in database")
            ignore_list.append(device_id)
        return

    # Update the device's flags
    db.ad_update(evt.addr, flags, evt.rssi)

    # If need to connect, add it to the list
    if db.should_connect():
        uwb_ble_connect.add(evt.addr, db)

def init():
    global scanner
    scanner = pi_ble_scanner.scanner(scan_cb)

    # Scan 80 out of 100 milliseconds
    err = scanner.set_timing(100, 80)

    # Filter ads for just our manufacturer ID and protocol ID
    err = scanner.filter_add(3, bytes([0x77, 0x00, 0x0c, 0x00]))

    print("BLE scanner initialized")

def start():
    global scanner
    err = scanner.start(0)
    print("BLE scanner started", err)

def stop():
    global scanner
    err = scanner.stop()
    print("BLE scanner stopped", err)
