app_id='pscan'
app_ver='1.1.1'

import canvas_ble
import binascii

canvas_ble.init()

def scan_init():
    global scanner
    scanner = canvas_ble.Scanner(scan_cb)
    # Filter ads for just our manufacturer ID and protocol ID
    err = scanner.filter_add(3, bytes([0x77, 0x00]))
    # Only enable 1M PHY for more responsive scan results
    scanner.set_phys(canvas_ble.PHY_1M)
    # Set scan window and interval to scan 100% of the time
    err = scanner.set_timing(100, 100)

def scan_cb(sr):
    print("DID={},RS={},AD={}".format(
        binascii.hexlify(sr.addr).decode(),
        sr.rssi, binascii.hexlify(sr.data).decode()))

scan_init()