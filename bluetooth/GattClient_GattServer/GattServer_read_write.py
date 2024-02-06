import canvas_ble as ble
import time


def s1c1_cb(event):
    if event.type == ble.GattServer.EVENT_ATTR_VALUE:
        print("Name: ", event.name)
        print("Data: ", event.data.decode())
        print("Connection", event.connection)
        print("Event", event.type)
        print("----------------")


def cb_con(conn):
    global disconnected
    disconnected = False
    print("Connected: ", conn)
    print("----------------")


def cb_disconnected(conn):
    global disconnected
    print("Disconnected: ", conn)
    disconnected = True
    advert.start()


gatt_table = {
    "Service 1": {
        "Name": "S1",
        "UUID": "b8d02d81-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1": {
            "Name": "S1:C1",
            "UUID": "b8d00001-6329-ef96-8a4d-55b376d8b25a",
            "Length": 20,
            "Read Encryption": "None",
            "Write Encryption": "None",
            "Capability": "Write",
            "Callback": s1c1_cb
        },
        "Characteristic 2": {
            "Name": "S1:C2",
            "UUID": "b8d00004-6329-ef96-8a4d-55b376d8b25a",
            "Length": 20,
            "Read Encryption": "None",
            "Write Encryption": "None",
            "Capability": "Read"
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
advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas Read/Write", False)
advert.set_properties(True, True, False)
advert.set_interval(200, 250)

def main_loop():
    print("")
    print("Gatt Server Read / Write example")
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
