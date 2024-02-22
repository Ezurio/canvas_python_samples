import canvas_ble as ble

ble_name = "Canvas BLE"
service_uuid = "11223344-5566-7788-99aa-bbccddeeff00"
char_uuid = "00000001-5566-7788-99aa-bbccddeeff00"

def cb_con(conn): # Connect callback
    print("Connected")

def cb_discon(conn): # Disconnect callback
    global advert
    print("Disconnected")
    advert.start()

def cb_write(event_object):
    print('Received message: ' + event_object.data.decode())

def uuidToBytes(uuid): # Convert the 128 bit UUID string to bytes
    uuid_bytes = list(bytes.fromhex(uuid.replace("-", "")))
    uuid_bytes.reverse()
    return bytes(uuid_bytes)

# GATT table definition for a service with a writable "message" characteristic
gatt_table = { 
    "Service 1":{
        "Name": "My BLE Service",
        "UUID": service_uuid,
        "Characteristic 1":{
            "Name": "message",
            "UUID" : char_uuid,
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Write",
            "Callback" : cb_write
        }
    }
}

# Initialize the BLE stack and set the connection and disconnection callbacks
ble.init()
ble.set_periph_callbacks(cb_con, cb_discon)

# Start advertising our primary service by the 128 bit UUID
advert = ble.Advertiser()
advert.stop()
advert.clear_buffer(False)
advert.add_ltv(1, bytes([6]), False)
advert.add_ltv(7, uuidToBytes(service_uuid), False)
advert.add_tag_string(9, ble_name, False)
advert.set_phys(ble.PHY_1M, ble.PHY_2M)
advert.set_properties(True, False, True)
advert.set_interval(240, 250)
advert.start()

# Define the gatt server and callbacks and start the GATT server
my_gattserver = ble.GattServer()
my_gattserver.build_from_dict(gatt_table)
my_gattserver.start()
