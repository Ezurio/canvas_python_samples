import canvas_ble, time, binascii
# Initialize the canvas_ble module
canvas_ble.init()
# Callback function to handle scan results
def scan_result_cb(e):
    # print the advertisement scan result data
    print(canvas_ble.addr_to_str(e.addr)[2:], "RSSI: ", "{:4}".format(e.rssi), " Data: ", e.data.hex())

# Create a Scanner object with the callback function
s = canvas_ble.Scanner(scan_result_cb)
# Add an address filter to the scanner
filter_address = "7CC6B69155D1"  # Replace with the desired address to filter
s.filter_add(canvas_ble.Scanner.FILTER_ADDR, bytes(reversed(binascii.unhexlify(filter_address + '00'))))
# Start scanning with the Scanner object
active_scan = True  # Set to True for active scanning, False for passive scanning
s.start(active_scan)
# Delay for 5 seconds to allow scanning
time.sleep(5)
# Stop scanning
s.stop()
s.filter_reset()

