from Beacons import Eddystone_UID
import time
import canvas_ble as ble

# Use the 'Beacons' python module to create and advertise an eddystone beacon
print('Eddystone UID Beacon Advertisment')

ranging_data = 10
namespace = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09]
beacon = [20, 21, 22, 23, 24, 25]
my_eddystone_uid = Eddystone_UID(namespace, beacon, ranging_data)

print("UID Beacon Data: ", my_eddystone_uid.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
data = bytes(my_eddystone_uid.get_beacon())
advert.add_data(data, False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

print("Finished")