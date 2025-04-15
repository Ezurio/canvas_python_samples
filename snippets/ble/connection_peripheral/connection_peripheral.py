import canvas_ble as ble

connection = None  # Initialize the connection variable to None
peripheral_name_prefix = "Canvas-"  # The prefix of this device's name

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

