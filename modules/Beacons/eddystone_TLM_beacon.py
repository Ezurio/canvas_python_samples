from Beacons import Eddystone_TLM
import canvas_ble as ble

# Use the 'Beacons' python module to create and advertise an eddystone beacon
print('Eddystone TLM Beacon Advertisment')

temperature = 22
battery = 3300
encrypted = False
my_eddystone_tlm = Eddystone_TLM(encrypted, battery, temperature)
print("TLM Beacon Data: ", my_eddystone_tlm.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
data = bytes(my_eddystone_tlm.get_beacon())
advert.add_data(data, False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

print("Finished")