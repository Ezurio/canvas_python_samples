import canvas_ble as ble
from canvas_ble import UUID
import time


def s1c1_cb(event):
    if event.type == ble.GattServer.EVENT_ATTR_VALUE:
        print("Event", event.type)
        print("Name: ", event.name)
        print("Data: ", event.data.decode())
        print("Data Hex: ", event.data.hex())
        print("Connection", event.connection)


def generic_cb(event):
    print("Event", event.type)
    print("Name: ", event.name)
    if event.data is not None:
        print("Data: ", event.data.decode())
        print("Data Hex: ", event.data.hex())
    if event.connection is not None:
        print("Connection", event.connection)


def cb_con(conn):
    global disconnected
    disconnected = False
    print("Connected: ", conn)
    print("----------------")


def cb_disconnected(conn):
    global advert, disconnected
    print("Disconnected: ", conn)
    disconnected = True
    if advert is not None:
        advert.start()


gatt_table = {
    UUID("b8d02d81-6329-ef96-8a4d-55b376d8b25a"): {
        UUID("b8d00001-6329-ef96-8a4d-55b376d8b25a"): {
            "name": "S1:C1",
            "length": 20,
            "flags": ble.GattServer.FLAG_WRITE_ACK,
            "callback": s1c1_cb
        },
        UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"): {
            "name": "S1:C2",
            "length": 20,
            "flags": ble.GattServer.FLAG_READ | ble.GattServer.FLAG_NOTIFY | ble.GattServer.FLAG_INDICATE,
            "callback": generic_cb
        }
    }
}

# Set callbacks before starting to advertise
disconnected = True
ble.set_periph_callbacks(cb_con, cb_disconnected)
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)

# Configure advertisements
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(True)
advert.add_canvas_data(0, 0, True)
advert.clear_buffer(False)
advert.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE,
                      "Canvas Read/Write/Sub", False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)


def main_loop():
    print("")
    print("Gatt Server Read / Write / Subscribe example")
    print("BLE address: ", ble.addr_to_str(ble.my_addr()))
    my_gattserver.start()
    advert.start()
    loop = 0
    while True:
        time.sleep_ms(1000)
        if disconnected:
            loop = 0
        else:
            loop = loop + 1
            string = "Count: %d" % (loop)
            value = bytes(string, 'utf-8')
            print(string)
            my_gattserver.write("S1:C2", value)


main_loop()
