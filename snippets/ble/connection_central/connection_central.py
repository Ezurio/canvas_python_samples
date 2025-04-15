import canvas_ble as ble
import time

connection = None  # Initialize the connection variable to None
peripheral_name_prefix = "Canvas-"  # The prefix of the device name we want to connect to
peripheral_address = None  # This will hold the address of the peripheral we want to connect to

def connected_cb(conn):
    global connection
    connection = conn  # Save the connection object for later use
    print("Connection established with", ble.addr_to_str(peripheral_address)[2:])  # Print the connected device's address

def disconnected_cb(conn):
    print("Disconnected from", ble.addr_to_str(peripheral_address)[2:])

def parse_name_from_advertisement(advertisement_data):
    # Iterate through the advertisement fields to find the device name
    for i in range(len(advertisement_data)):
        ltv_len = advertisement_data[i]  # Length of the field
        if ltv_len == 0 or i + 2 >= len(advertisement_data):
            continue
        # The type of the field (AD Type)
        ltv_type = advertisement_data[i + 1]
        if ltv_type == ble.AD_TYPE_NAME_COMPLETE or ltv_type == ble.AD_TYPE_NAME_SHORT:
            # The actual name data follows the length and type bytes
            name_bytes = advertisement_data[i + 2:i + 2 + ltv_len - 1]
            return name_bytes.decode('utf-8')
    
    return None  # Return None if no name found in the advertisement data

def scan_cb(e):
    # If a connectable advertisement is found with a device name starting
    # with the peripheral_name_prefix, save the address for connection.
    global peripheral_address, scanner
    if e.data.find(peripheral_name_prefix.encode()) > -1:
        if peripheral_address is None:
            # Save the address of the peripheral found
            peripheral_address = e.addr
            print("Found peripheral '" + parse_name_from_advertisement(e.data) + "' (" + ble.addr_to_str(peripheral_address)[2:] + ")")
            scanner.stop()

ble.init()
# Scan for a device with name starting with the peripheral_name_prefix
scanner = ble.Scanner(scan_cb)
scanner.start(True)  # Start scanning with active scan

wait_time = 0
print("Scanning 10 sec. for devices with name starting with:", peripheral_name_prefix)
while peripheral_address is None:
    # Keep the main thread alive while scanning for the peripheral
    # This allows the scanner to process events and call the callback
    time.sleep_ms(100)  # Sleep to prevent busy waiting, allowing other tasks to run
    wait_time += 100
    if wait_time >= 10000:
        # Timeout after 10 seconds if no device found
        print("Timeout waiting for device with prefix", peripheral_name_prefix)
        break

scanner.stop()  # Stop scanning

# if no peripheral was found, exit the script
if peripheral_address is None:
    print("No device found with prefix", peripheral_name_prefix)
    print("Exiting script.")
else:
    # Now that we have the peripheral address, connect to it
    print("Attempting to connect to peripheral with address", ble.addr_to_str(peripheral_address)[2:])
    # Create a connection to the peripheral using the address found during scanning
    connection = ble.connect(peripheral_address, ble.PHY_1M, connected_cb, disconnected_cb)
    # Delay to allow the connection to establish and callbacks to be processed
    time.sleep(5)
    # Disconnect from the peripheral when done
    connection.disconnect()
    time.sleep(1)  # Give some time to ensure the disconnect callback is processed
    # Ensure the connection is cleaned up properly
    del(connection)

