import canvas_ble
from canvas_ble import UUID
import time

scanner = None
connection = None
gatt_client = None


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
    scanner.filter_add(scanner.FILTER_NAME, "nRF Connect".encode())
    scanner.start(1)


def cb_notify_ind(event):
    type = "Notify" if event.notify else "Indicate"
    print(type + " from UUID: ", event.uuid, " Name: ",
          event.name, " Data: ", event.data.hex())


start_scanning()

print("Waiting for connection")
while connection == None:
    time.sleep_ms(1000)

gatt_client = canvas_ble.GattClient(connection)
gatt_client.set_callback(cb_notify_ind)
gatt_client.discover()

# Subscribe to TX power characteristic using a name
gatt_client.set_name(UUID(0x2a07), "tx_power")
# Subscribe to notifications
gatt_client.subscribe("tx_power", True, False)
# Other options
# Subscribe to indications
# gatt_client.subscribe("tx_power", False, True)
# Subscribe to both notifications and indications
# gatt_client.subscribe("tx_power", True, True)
# Unsubscribe from notifications and indications
# gatt_client.subscribe("tx_power", False, False)
