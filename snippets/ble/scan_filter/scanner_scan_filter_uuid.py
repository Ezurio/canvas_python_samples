import canvas_ble, time
from canvas_ble import UUID
# Initialize the canvas_ble module
canvas_ble.init()
# Callback function to handle scan results
def scan_result_cb(e):
    # print the advertisement scan result data
    print(canvas_ble.addr_to_str(e.addr)[2:], "RSSI: ", "{:4}".format(e.rssi), " Data: ", e.data.hex())

# Create a Scanner object with the callback function
s = canvas_ble.Scanner(scan_result_cb)
# Add a uuid filter to the scanner
filter_uuid = UUID('6e400001-b5a3-f393-e0a9-e50e24dcca9e')  # Example UUID
s.filter_add(canvas_ble.Scanner.FILTER_UUID, bytes(filter_uuid))
# Start scanning with the Scanner object
active_scan = True  # Set to True for active scanning, False for passive scanning
s.start(active_scan)
# Delay for 5 seconds to allow scanning
time.sleep(5)
# Stop scanning
s.stop()
s.filter_reset()

