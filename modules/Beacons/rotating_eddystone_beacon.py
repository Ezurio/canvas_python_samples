from Beacons import Eddystone_UID
from Beacons import Eddystone_URL
from Beacons import Eddystone_TLM
import canvas
import canvas_ble as ble

print("Implement a rotating Eddystone beacon")
print("This allows a beacon to advertise position, URL and Telemetry")

ranging_data = -24
namespace = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09]
beacon = [20, 21, 22, 23, 24, 25]
temperature = 22
battery = 3300
current_object = 0

# Create initial adverts
eddy_url = Eddystone_URL('https://lairdconnect.com', ranging_data)
eddy_uri = Eddystone_UID(namespace, beacon, ranging_data)
eddy_tlm = Eddystone_TLM(False, battery, temperature)

eddy_objects = [eddy_url,eddy_uri,eddy_tlm]

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
data = bytes(eddy_url.get_beacon())
advert.add_data(data, False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
advert.start()

# Callback to cycle the advert
def callback(event):
    global advert
    global eddy_objects
    global current_object

    if current_object == 2:
        battery = event["battery"]
        temperature = event["temperature"]
        eddy_objects[current_object].update(battery, temperature)

    advert.clear_buffer(False)
    data = bytes(eddy_objects[current_object].get_beacon())
    advert.add_data(data, False)
    advert.update()

    current_object += 1
    if current_object > 2:
        current_object = 0

# Event data global object
event_data = {"temperature":temperature,
              "battery": battery}

# Initialise the timer to fire every 2.5 seconds, be repeating and have event data
timer = canvas.Timer(2500, True, callback, event_data)

# Start the timer
timer.start()
