from ibeacon import iBeacon
import canvas_ble as ble

print('iBeacon Beacon Advertisment')

my_iBeacon = iBeacon('01020304-0102-0102-0102-010203040506', 0x0102, 0x0304, -50)

print(my_iBeacon.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.clear_buffer(False)
data = bytes(my_iBeacon.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, False, False)
advert.set_interval(200, 250)
advert.start()
