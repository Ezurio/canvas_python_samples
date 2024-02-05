import canvas_ble as ble
import time

SIZE_IN_BYTES = 4

def dual_cb(event):
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
    "Farm Truck Service": {
        "Name": "dually",
        "UUID": "d90d8245-8885-4b4b-9a6e-988de00922a8",
        "Characteristic 1": {
            "Name": "decrement",
            "UUID": "d90d8245-8886-4b4b-9a6e-988de00922a8",
            "Length": SIZE_IN_BYTES,
            "Read Encryption": "None",
            "Write Encryption": "None",
            "Capability": ["Read", "Write"],
            "Callback": dual_cb
        },
    }
}

# Set callbacks before starting to advertise
disconnected = True
ble.set_periph_callbacks(cb_con, cb_disconnected)
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)

# Setup advertisement with "Canvas" as the name.
flags = [6]
my_bytes=bytes(flags)
ble.init()
adv = ble.Advertiser()
adv.stop()
adv.clear_buffer(False)
adv.add_ltv(1, my_bytes, False)
adv.add_tag_string(9, "Canvas", False)
adv.set_phys(ble.PHY_1M, ble.PHY_1M)
adv.set_properties(True, True, False)
adv.set_interval(240, 250)

def main_loop():
    print("")
    print("Gatt Server Read and Write example")
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
                my_gattserver.write("decrement", value.to_bytes(SIZE_IN_BYTES, 'little'))

main_loop()
