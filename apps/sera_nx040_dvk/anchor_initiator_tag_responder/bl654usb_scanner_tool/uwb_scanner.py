import canvas_ble as ble
import time

#
# UWB Range Reporting via BLE Advertisements
#
# This script scans for advertisements from "Tag" devices implementing the
# UWB Anchor Initiator/Tag Responder application script.
# 
# This script is intended for use on a BL654 USB adapter and will scan
# for advertisements from the "Tag" devices and print range data.
#
# Tag devices implement protocol 0x000C and contain manufacturer specific 
# data elements with company ID 0x0077 (Ezurio/Laird Connectivity).
# The Tag's local short address is included as the "local" parameter and
# each Anchor's short address is displayed with corresponding range in cm.
#

def scan_cb(evt):
    i = 0
    while i < len(evt.data):
        data_element_len = evt.data[i]
        if evt.data[i+1] == 0xff:
            # Manufacturer Specific Data
            i+=2
            local_addr_str = hex(evt.data[i+9])[2:] + hex(evt.data[i+8])[2:]
            json_str = '{' + '"local":"' + local_addr_str + '",'
            j = i + 20
            while j < (i+data_element_len-2):
                tag_id = evt.data[j]
                tag_len = evt.data[j+1]
                if tag_id == 0x00:
                    peer_id_str = hex(evt.data[j+2])[2:] + hex(evt.data[j+3])[2:]
                    range = (evt.data[j+5] << 8) | (evt.data[j+4])
                    json_str += '"' + peer_id_str + '":' + str(range)
                    if (j+6) < (i+data_element_len-2):
                        json_str += ','
                j += 2 + tag_len
            json_str += '}'
            print(json_str)
            break
        i += data_element_len + 1
    return 0

filter = b'\x77\x00\x0C\x00'

print("Initialize Scanner")
ble.init()
s = ble.Scanner(scan_cb)
s.set_timing(100, 100)
s.filter_add(ble.Scanner.FILTER_MANUF_DATA, filter)

# Start scanning
s.start(0)

#NOTE: To stop scanning, type s.stop() at the REPL prompt
