import canvas_ble, time
# Initialize the canvas_ble module
canvas_ble.init()
# Callback function to handle scan results
def scan_result_cb(e):
    # print the advertisement scan result data
    print(canvas_ble.addr_to_str(e.addr)[2:], "RSSI: ", "{:4}".format(e.rssi), " Data: ", e.data.hex())

# Create a Scanner object with the callback function
s = canvas_ble.Scanner(scan_result_cb)
# Add a data filter to the scanner
filter_data = bytes('ezurio.com', 'utf-8')  # Example data to filter
s.filter_add(canvas_ble.Scanner.FILTER_DATA, filter_data)
# Start scanning with the Scanner object
active_scan = True  # Set to True for active scanning, False for passive scanning
s.start(active_scan)
# Delay for 5 seconds to allow scanning
time.sleep(5)
# Stop scanning
s.stop()
s.filter_reset()

