import canvas_ble as ble
import time

print("Peripheral connection example\r\n")

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas Basic Advert", False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)
advert.start()

dsc = False

connection = None

def cb_con(conn):
    global advert
    global connection
    connection = conn
    print("Connected ", connection)
    result = advert.stop()
    rssi = connection.get_rssi()
    print("RSSI = ", rssi)


def cb_discon(conn):
    global dsc
    print("Disconnected")
    dsc = True

ble.set_periph_callbacks(cb_con, cb_discon)
