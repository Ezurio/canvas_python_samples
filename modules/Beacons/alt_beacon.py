from Beacons import AltBeacon
import canvas_ble as ble

# Use the 'Beacons' python module to create and advertise an eddystone beacon
print('altBeacon Beacon Advertisment')

mfg_id = 0x0077
beacon_id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3 , 4, 5]
beacon_data = [20, 21, 22, 23]
ranging_data  = -24
mfg_data = 42

my_altBeacon = AltBeacon(mfg_id, beacon_id, beacon_data, ranging_data, mfg_data)

print(my_altBeacon.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
data = bytes(my_altBeacon.get_beacon())
advert.add_data(data, False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

print("Finished")