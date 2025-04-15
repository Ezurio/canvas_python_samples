import canvas_ble
# Initialize the canvas_ble module
canvas_ble.init()
# Print the BLE address of the device
my_ble_addr = canvas_ble.addr_to_str(canvas_ble.my_addr())[2:]
print('My BLE Address:', my_ble_addr)
# Create an Advertiser object
advert = canvas_ble.Advertiser()
# Stop any existing advertisement
advert.stop()
# Clear the scan response buffer and add default Canvas data to it
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
# Clear the advertisement buffer
advert.clear_buffer(False)
# Add advertisement data
advert.add_ltv(canvas_ble.AD_TYPE_FLAGS, bytes([6]), False)
# Add a data element to the advertisement data
uri_data = 'ezurio.com'  # Example URI data
advert.add_ltv(0x24, bytes([0x17, 0x2F, 0x2F]) + bytes(uri_data,'utf-8'), False)
# Set the PHYs and properties for the advertisement
advert.set_phys(canvas_ble.PHY_1M, canvas_ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
# Start advertising
advert.start()
print('Advertising started with URI  data:', uri_data)
# To stop advertising, type `advert.stop()` in the console

