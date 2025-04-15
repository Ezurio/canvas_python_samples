from eddystone import Eddystone_URL
import canvas_ble as ble

print('Eddystone Beacon Advertisment')

my_eddystone = Eddystone_URL('https://ezurio.com', 10)
print(my_eddystone.get_beacon())

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.clear_buffer(False)
# Set the advertising data to the Eddystone URL data
data = bytes(my_eddystone.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, False, False)
advert.set_interval(200, 250)
advert.start()
