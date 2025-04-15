import canvas_ble as ble
from canvas_ble import UUID

connection = None  # Initialize the connection variable to None
peripheral_name_prefix = "Canvas-"  # The prefix of this device's name
gatt_server = None  # Initialize the GATT server variable to None

def cb_nus_rx(event):
    """
    Callback function for receiving data on the RX characteristic.
    This function will be called when data is written to the RX characteristic.
    """
    if event.data:
        print("Received data on RX:", event.data.decode('utf-8', 'ignore'))
        # For testing, echo the received data back to the TX characteristic
        if connection:
            # Notify the connected device with the received data
            # This is a placeholder for the actual notification logic
            print('Echoing back to TX:', event.data.decode('utf-8', 'ignore'))
            gatt_server.notify(connection, UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e'), event.data)
    else:
        print("Received empty data on RX")

def cb_nus_tx(event):
    """
    Callback function for sending notifications on the TX characteristic.
    This function will be called when the TX characteristic is accessed for notification.
    """
    if event.data:
        print("Sending notification on TX:", event.data.decode('utf-8', 'ignore'))
    else:
        print("Sending empty notification on TX")
    # In a real application, you might want to send some data back or process it further

def start_gatt_server():
    global gatt_dict, gatt_server
    gatt_dict = {
        UUID('6e400001-b5a3-f393-e0a9-e50e24dcca9e'): {
            UUID('6e400002-b5a3-f393-e0a9-e50e24dcca9e'): {
                "name": "RX",
                "flags": ble.GattServer.FLAG_WRITE_NO_ACK,
                "length": 200,
                "callback": cb_nus_rx
            },
            UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e'): {
                "name": "TX",
                "flags": ble.GattServer.FLAG_NOTIFY,
                "length": 200,
                "callback": cb_nus_tx
            }
        }
    }
    gatt_server = ble.GattServer()
    gatt_server.build_from_dict(gatt_dict)  # Build the GATT server from the dictionary
    gatt_server.start()  # Start the GATT server

# Initialize the canvas_ble module
ble.init()
# Create an Advertiser object to start advertising
advert = ble.Advertiser()
advert.stop()
# Clear the scan response buffer
advert.clear_buffer(True)
# Clear the default ad buffer and set flags and name for the advertisement
advert.clear_buffer(False)
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
# Append last 4 digits of the BLE address to BLE name to add uniqueness
peripheral_name_prefix += ble.addr_to_str(ble.my_addr())[2:][-4:]
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, peripheral_name_prefix, False)
# Set properties for the advertiser (connectable, scannable, extended)
advert.set_properties(True, True, False)
# Set the interval for advertising (in ms)
advert.set_interval(200, 250)
# Start the GATT server
start_gatt_server()
# Start advertising
advert.start()

def connected_cb(conn):
    global connection
    connection = conn  # Save the connection object for later use
    print("Connection established with", ble.addr_to_str(conn.get_addr())[2:]) # Print the connected device's address
    advert.stop()

def disconnected_cb(conn):
    global connection
    print("Disconnected from", ble.addr_to_str(conn.get_addr())[2:])
    advert.start()  # Restart advertising when disconnected
    del(connection)  # Clean up the connection reference
    connection = None  # Reset the connection variable

ble.set_periph_callbacks(connected_cb, disconnected_cb)

