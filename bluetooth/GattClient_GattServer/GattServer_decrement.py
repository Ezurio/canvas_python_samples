import canvas_ble as ble
from canvas_ble import UUID
import time

SIZE_IN_BYTES = 4


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
    global disconnected
    print("Disconnected: ", conn)
    disconnected = True
    # Should be defined by application script
    try:
        global adv
        if adv is not None:
            adv.start()
    except:
        pass


# Create a characteristic that is readable and writable
gatt_table = {
    UUID("d90d8245-8885-4b4b-9a6e-988de00922a8"): {
        UUID("d90d8245-8886-4b4b-9a6e-988de00922a8"): {
            "name": "decrement",
            "length": SIZE_IN_BYTES,
            "flags": ble.GattServer.FLAG_WRITE_ACK | ble.GattServer.FLAG_READ,
            "callback": generic_cb
        },
    }
}

# Set callbacks before starting to advertise
disconnected = True
ble.set_periph_callbacks(cb_con, cb_disconnected)
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)

# Setup advertisement with "Canvas" as the name.
ble.init()
adv = ble.Advertiser()
adv.stop()
adv.clear_buffer(True)
adv.add_canvas_data(0, 0, True)
adv.clear_buffer(False)
adv.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
adv.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas", False)
adv.set_properties(True, True, False)
adv.set_interval(200, 250)


def main_loop():
    print("")
    print("Gatt Server decrement example")
    print("BLE address: ", ble.addr_to_str(ble.my_addr()))
    my_gattserver.start()
    adv.start()
    while True:
        time.sleep_ms(1000)
        if disconnected:
            pass
        else:
            value = int.from_bytes(my_gattserver.read("decrement"), 'little')
            if value != 0:
                value -= 1
                print(value)
                my_gattserver.write(
                    "decrement", value.to_bytes(SIZE_IN_BYTES, 'little'))


main_loop()
