from Beacons import iBeacon
import canvas_ble as ble

# Use the 'Beacons' python module to create and advertise an eddystone beacon
print('iBeacon Beacon Advertisment')

my_iBeacon = iBeacon('01020304-0102-0102-0102-010203040506', 0x0102, 0x0304, 10)

print(my_iBeacon.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
data = bytes(my_iBeacon.get_beacon())
advert.add_data(data, False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

print("Finished")