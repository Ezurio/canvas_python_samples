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
ble_name = "Scan Filter Ad"
advert.add_tag_string(canvas_ble.AD_TYPE_NAME_COMPLETE, ble_name, False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
# Start advertising
advert.start()
print('Advertising started with name:', ble_name)

