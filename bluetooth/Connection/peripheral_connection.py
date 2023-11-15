import canvas_ble as ble
import time

print("Peripheral connection example\r\n")

# Setup flag byte array
flags = [6]
flag_bytes=bytes(flags)

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
advert.add_ltv(1, flag_bytes, False)
advert.add_tag_string(9, "Canvas Basic Advert", False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
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
