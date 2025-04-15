import canvas_ble as ble
# Initialize the canvas_ble module
ble.init()
# Print the BLE address of the device
my_ble_addr = ble.addr_to_str(ble.my_addr())[2:]
print('My BLE Address:', my_ble_addr)
# Create an Advertiser object
advert = ble.Advertiser()
# Stop any existing advertisement
advert.stop()
# Clear the scan response buffer and add default Canvas data to it
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
# Clear the advertisement buffer
advert.clear_buffer(False)
# Add advertisement data
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
ble_name = "Canvas-" + my_ble_addr[-4:]
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, ble_name, False)
# Set the PHYs and properties for the advertisement
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
# Start advertising
advert.start()
print('Advertising started with name:', ble_name)
# To stop advertising, type `advert.stop()` in the console

