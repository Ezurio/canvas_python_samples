import canvas_ble as ble
from canvas_ble import UUID
import time

print("")
print("Gatt Server Notify Example")
print("")

# --------------------------------------
# Variables
# --------------------------------------
connection = None
discon = False
do_notify = False
count = 0

# --------------------------------------
# Callbacks
# --------------------------------------
def cb_notify_enabled(event_object):
    global do_notify
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        print(event_object.name, " disabled")
        print("----------------")
        do_notify = False

    if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
        print(event_object.name, " notify enabled")
        print("----------------")
        do_notify = True

    if event_object.type == ble.GattServer.EVENT_CCCD_INDICATE:
        print(event_object.name, " indicate enabled - THIS IS BAD")
        print("----------------")

    if event_object.type == ble.GattServer.EVENT_CCCD_BOTH:
        print(event_object.name, " notify and indicate enabled - THIS IS BAD")
        print("----------------")


def cb_con(conn):
    global connection
    connection = conn
    print("Connected: ", connection)
    print("-----------------")


def cb_discon(conn):
    global discon
    print("Disconnected: ")
    print("-----------------")
    discon = True


# GATT table definition
gatt_table = {
    UUID("b8d02d81-6329-ef96-8a4d-55b376d8b25a"): {
        UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"): {
            "name": "S1:C1",
            "length": 20,
            "flags": ble.GattServer.FLAG_NOTIFY,
            "callback": cb_notify_enabled
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
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas Notify", False)
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

# Loop until a disconnection occurrs
while discon == False:
    # Wait for 500 ms
    time.sleep_ms(500)
    # If a connection has been made
    if connection != None and do_notify:
        # Update the counter
        count = count + 1
        # Create a message
        string = "Count: %d" % (count)
        print(string)
        value = bytes(string, 'utf-8')
        # Notify the connected client
        try:
            my_gattserver.notify(connection, "S1:C1", value)
        except:
            print("Notify error")

# Delete the connection once it's disconnected.
del (connection)
