import time
import canvas_ble as ble

# Initial message describing demo
print('Scan Filter Advertisment')

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Scan Filter Ad", False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
advert.start()
