from eddystone import Eddystone_TLM
import canvas_ble as ble

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
advert.clear_buffer(True)
advert.clear_buffer(False)
# Set the advertising data to the Eddystone TLM data
data = bytes(my_eddystone_tlm.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, False, False)
advert.set_interval(200, 250)
advert.start()
