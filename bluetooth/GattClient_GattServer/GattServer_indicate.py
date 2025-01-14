import canvas_ble as ble
from canvas_ble import UUID
import time

print("")
print("Gatt Server Indication Example")
print("")

# --------------------------------------
# Callbacks
# --------------------------------------
def cb_con(conn):
    global connection
    connection = conn
    print("Connected: ", connection)
    print("-----------------")


def cb_discon(conn):
    global discon
    print("Disconnected: ", connection)
    print("-----------------")
    discon = True


def cb_indicate(event_object):
    global do_indicate
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        do_indicate = False
        print(event_object.name, " disabled")
        print("----------------")
    if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
        do_indicate = False
        print(event_object.name, " notify enabled - THIS IS BAD")
        print("----------------")
    if event_object.type == ble.GattServer.EVENT_CCCD_INDICATE:
        do_indicate = True
        print(event_object.name, " indicate enabled")
        print("----------------")
    if event_object.type == ble.GattServer.EVENT_CCCD_BOTH:
        do_indicate = True
        print(event_object.name, " notify and indicate enabled - THIS IS BAD")
        print("----------------")
    if event_object.type == ble.GattServer.EVENT_INDICATION_OK:
        print("Indication ACK ", event_object.name)
        print("----------------")
    if event_object.type == ble.GattServer.EVENT_INDICATION_TIMEOUT:
        print("Indication Timeout!")
        print("----------------")
        event_object.connection.disconnect()


# --------------------------------------
# Variables
# --------------------------------------
connection = None
discon = False
do_indicate = False
loop = 0

gatt_table = {
    UUID("b8d02d81-6329-ef96-8a4d-55b376d8b25a"): {
        UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"): {
            "name": "S1:C1",
            "length": 20,
            "flags": ble.GattServer.FLAG_INDICATE,
            "callback": cb_indicate
        }
    }
}

# --------------------------------------
# Application script
# --------------------------------------
# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas Indicate", False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
advert.start()

# Define the gatt server and callbacks
ble.set_periph_callbacks(cb_con, cb_discon)
print("Build Dictionary")
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)

# Start the GATT server
print("Starting GATT server")
my_gattserver.start()
print("-----------------")

# Loop until a disconnection occurs
while discon == False:
    time.sleep_ms(1000)
    if connection != None and do_indicate:
        loop = loop + 1
        string = "Count: %d" % (loop)
        value = bytes(string, 'utf-8')
        try:
            my_gattserver.indicate(connection, "S1:C1", value)
        except:
            print("Indicate failed")

del (connection)
