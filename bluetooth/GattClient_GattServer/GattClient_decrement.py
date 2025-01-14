import canvas_ble
from canvas_ble import UUID
import time

SIZE_IN_BYTES = 4

scanner = None
connection = None
gatt_client = None

# In this setup, if the remote devices makes the connection,
# the connection handle will be invalid.


def ble_connected(conn):
    global connection
    connection = conn
    print('Connected to', canvas_ble.addr_to_str(conn.get_addr()))


def ble_disconnected(conn):
    global scanner
    global connection
    global gatt_client
    connection = None
    gatt_client = None
    print('Disconnected from', canvas_ble.addr_to_str(conn.get_addr()))
    time.sleep_ms(5000)
    print("Restarting scan")
    scanner.start(1)


def scan_result(result):
    global scanner
    print('Connecting to', canvas_ble.addr_to_str(result.addr))
    scanner.stop()
    canvas_ble.connect(result.addr, canvas_ble.PHY_1M,
                       ble_connected, ble_disconnected)


def start_scanning():
    global scanner
    print("Starting scan")
    canvas_ble.init()
    scanner = canvas_ble.Scanner(scan_result)
    scanner.filter_reset()
    scanner.filter_add(scanner.FILTER_NAME, "Canvas".encode())
    scanner.start(1)


def cb_notify_ind(event):
    type = "Notify" if event.notify else "Indicate"
    print(type + " from UUID: ", event.uuid, " Name: ",
          event.name, " Data: ", event.data.decode('utf-8'))


read_value = bytearray(SIZE_IN_BYTES)
start_scanning()

print("Waiting for connection")
while connection == None:
    time.sleep_ms(1000)

gatt_client = canvas_ble.GattClient(connection)
gatt_client.set_callback(cb_notify_ind)
gatt_client.discover()

gatt_client.set_name(UUID("d90d8245-8886-4b4b-9a6e-988de00922a8"), "decr")
value = 10
gatt_client.write("decr", value.to_bytes(SIZE_IN_BYTES, 'little'))
time.sleep_ms(5000)
gatt_client.read("decr", read_value)
print("Read value: ", int.from_bytes(read_value, 'little'))
