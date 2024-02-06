from Beacons import Eddystone_EID
import canvas_ble as ble

# Use the 'Beacons' python module to create and advertise an eddystone beacon
print('Eddystone EID Beacon Advertisment')

ranging_data = 10
eid = [1,2,3,4,5,6,7,8]
my_eddystone_eid = Eddystone_EID(eid, ranging_data)
print("EID Beacon Data: ", my_eddystone_eid.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
data = bytes(my_eddystone_eid.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
advert.start()

print("Finished")