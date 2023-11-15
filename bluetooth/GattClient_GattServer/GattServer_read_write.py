import canvas_ble as ble
import time

print("")
print("Gatt Server Read / Write example")
print("")

print("BLE address: ", ble.addr_to_str(ble.my_addr()))

connection = None
discon = False

# Setup flag byte array
flags = [6]
flag_bytes=bytes(flags)

# Start an advert
ble.init()
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
advert.add_ltv(1, flag_bytes, False)
advert.add_tag_string(9, "Canvas Read/Write", False)
advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_properties(True, True, False)
advert.set_interval(250, 250)
advert.start()

def s1c1_cb(event):
    if event.type == ble.GattServer.EVENT_ATTR_VALUE:
        print("Name: ", event.name)
        print("Data: ", event.data.decode())
        print("Connection", event.connection)
        print("Event", event.type)
        print("----------------")

def cb_con(conn):
    global connection
    connection = conn
    print("Connected: ", connection)
    print("----------------")

def cb_discon(conn):
    global connection
    global discon
    print("Disconnected: ", connection)
    discon = True

gatt_table = {
    "Service 1":{
        "Name": "S1",
        "UUID":"b8d02d81-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1":{
            "Name": "S1:C1",
            "UUID" :"b8d00001-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Write",
            "Callback" : s1c1_cb
        },
        "Characteristic 2":{
            "Name": "S1:C2",
            "UUID" :"b8d00004-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read"
        }
    }
}

ble.set_periph_callbacks(cb_con, cb_discon)
print("Build Dictionary")
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)

print("Starting GATT server")
my_gattserver.start()
print("\n-------------\n\n")

loop = 0
while discon == False:
    time.sleep_ms(500)
    
    if connection != None:
        loop = loop + 1
        string = "Count: %d" %(loop)
        value = bytes(string, 'utf-8')
        print(string)
        my_gattserver.write("S1:C2", value)

del(connection)