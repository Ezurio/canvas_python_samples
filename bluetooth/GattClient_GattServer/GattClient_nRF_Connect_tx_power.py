import canvas_ble
import time

scanner = None
connection = None
gatt_client = None

# In this setup, if the remote devices makes the connection, 
# the connection handle will not be valid.
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


def cb_notify(event):
    print("Notify from UUID: ", event.uuid, " Name: ",
          event.name, " Data: ", event.data.hex())


def cb_indicate(event):
    print("Indicate from UUID: ", event.uuid, " Name: ",
          event.name, " Data: ", event.data.hex())

start_scanning()

print("Waiting for connection")
while connection == None:
    time.sleep_ms(1000)

gatt_client = canvas_ble.GattClient(connection)
gatt_client.set_callbacks(cb_notify, cb_indicate)
gatt_client.discover()

# Subscribe to TX power characteristic using a name
gatt_client.set_name("2a07", "tx_power")
gatt_client.configure_subscription("tx_power", canvas_ble.GattClient.CCCD_STATE_NOTIFY)
# Other options
#gatt_client.configure_subscription("tx_power", canvas_ble.GattClient.CCCD_STATE_INDICATE)
#gatt_client.configure_subscription("tx_power", canvas_ble.GattClient.CCCD_STATE_BOTH)
#gatt_client.configure_subscription("tx_power", canvas_ble.GattClient.CCCD_STATE_DISABLE)
