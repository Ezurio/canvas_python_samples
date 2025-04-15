from eddystone import Eddystone_UID
import canvas_ble as ble

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
advert.clear_buffer(True)
advert.clear_buffer(False)
# Set the advertising data to the Eddystone UID data
data = bytes(my_eddystone_uid.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, False, False)
advert.set_interval(200, 250)
advert.start()
