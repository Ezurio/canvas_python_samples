import time
import canvas_ble as ble

# Initial message describing demo
print('Scan Filter Advertisment')

# Setup flag byte array
flags = [6]
my_bytes=bytes(flags)

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
advert.add_ltv(1, my_bytes, False)
advert.add_tag_string(9, "Scan Filter Ad", False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

