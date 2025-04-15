import canvas_ble as ble
from canvas_ble import UUID
import time

connection = None  # Initialize the connection variable to None
peripheral_name_prefix = "Canvas-"  # The prefix of the device name we want to connect to
peripheral_address = None  # This will hold the address of the peripheral we want to connect to
gatt_client = None  # Initialize the GATT client variable to None
gatt_dict = None  # Initialize the GATT dictionary variable to None
notification_received = False  # Flag to indicate if a notification has been received

def notify_cb(event):
    global notification_received
    # Callback function to handle notifications from the peripheral
    if event.uuid == UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e'):
        # Check if the notification is from the TX characteristic
        if event.data:
            print("Notification received:", event.data.decode('utf-8', 'ignore'))
            notification_received = True
        else:
            print("Received empty notification")
    else:
        print("Notification received from unknown characteristic:", event.uuid)

def discover_cb(gc):
    global gatt_dict, gatt_client
    # Callback function to handle discovered services
    print("Discovered services:")
    gatt_dict = gatt_client.get_dict()  # Get the GATT dictionary from the client
    print(gatt_dict)  # Print the GATT dictionary
    # If the NUS service is found, enable notifications on the TX characteristic
    if UUID('6e400001-b5a3-f393-e0a9-e50e24dcca9e') in gatt_dict:
        print("NUS service found")
        # Enable notifications on the TX characteristic
        gatt_client.set_callback(notify_cb)
        gatt_client.subscribe(UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e'), True, False)
        gatt_client.write(UUID('6e400002-b5a3-f393-e0a9-e50e24dcca9e'), b'Hello from GATT client!')  # Write to the RX characteristic

def discover_services(conn):
    global gatt_client
    # Discover services on the connected device
    gatt_client = ble.GattClient(conn)
    gatt_client.discover(discover_cb)

def connected_cb(conn):
    global connection
    print("Connection established with", ble.addr_to_str(peripheral_address)[2:])  # Print the connected device's address
    connection = conn  # Save the connection object for later use

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

if peripheral_address is not None:
    # Now that we have the peripheral address, connect to it
    print("Attempting to connect to peripheral with address", ble.addr_to_str(peripheral_address)[2:])
    # Create a connection to the peripheral using the address found during scanning
    ble.connect(peripheral_address, ble.PHY_1M, connected_cb, disconnected_cb)
    while connection is None:
        # Wait for the connection to be established
        time.sleep_ms(100)
    
    discover_services(connection)  # Discover services on the connected device
    # Wait for a notification to be received
    while not notification_received:
        # Keep the main thread alive while waiting for the notification
        time.sleep_ms(100)
    
    if connection:
        print("Disconnecting from peripheral")
        connection.disconnect()
        time.sleep(1)
        # Ensure the connection is cleaned up properly
        del(connection)

