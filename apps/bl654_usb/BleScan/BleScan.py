import canvas_ble as ble
import binascii
import time

service_uuid = "11223344-5566-7788-99aa-bbccddeeff00"
char_uuid = "00000001-5566-7788-99aa-bbccddeeff00"
peripheral_device_address = None
connection = None
gatt_client = None

def uuidToBytes(uuid): # Convert the 128 bit UUID string to bytes
    uuid_bytes = list(bytes.fromhex(uuid.replace("-", "")))
    uuid_bytes.reverse()
    return bytes(uuid_bytes)

def scan_init():
    global scanner
    scanner = ble.Scanner(scan_cb)
    # Filter ads that contain manufacturer ID 0x0077
    scanner.filter_add(ble.Scanner.FILTER_UUID, uuidToBytes(service_uuid))
    scanner.set_timing(100, 100) # Set scan to 100% duty cycle

def scan_cb(sr):
    global peripheral_device_address
    print("DID={},RS={},AD={}".format(
        binascii.hexlify(sr.addr).decode(),
        sr.rssi, binascii.hexlify(sr.data).decode()))
    peripheral_device_address = sr.addr

def send(message):
    global gatt_client
    global char_uuid
    gatt_client.write(char_uuid, message)

def connection_cb(conn):
    global connection
    global gatt_client
    print("Connection established with {}".format(
        ble.addr_to_str(conn.get_addr())))
    connection = conn
    gatt_client = ble.GattClient(conn)
    gatt_client.discover()
    print('Discovering services...')
    send(b'Hello, BLE!')
    print('Writing to characteristic...')

def disconnection_cb(conn):
    print("Connection closed with {}".format(
        ble.addr_to_str(conn.get_addr())))

ble.init()
scan_init()
scanner.start(1)
print('Scanning for peripheral devices for 2 seconds...')
time.sleep_ms(2000)
scanner.stop()

if peripheral_device_address is not None:
    print("Client found, attempting connection to", ble.addr_to_str(peripheral_device_address))
    ble.connect(peripheral_device_address, ble.PHY_2M, connection_cb, disconnection_cb)
