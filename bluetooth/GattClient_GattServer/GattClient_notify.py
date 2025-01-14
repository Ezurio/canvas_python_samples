import canvas_ble as ble
from canvas_ble import UUID
import time

print("GATT Client Notify example\r\n")

connected = False


def cb_con(conn):
    global connected
    connected = True
    print("\r\nConnected\r\n")
    rssi = conn.get_rssi()
    print("RSSI = ", rssi)


def cb_discon(conn):
    print("\r\nDisconnected\r\n")
    global connected
    connected = False


def cb_notify_ind(event):
    type = "Notify" if event.notify else "Indicate"
    print(type + " from UUID: ", event.uuid, " Name: ",
          event.name, " Data: ", event.data.decode('utf-8'))


ble.init()

print("Connecting")
address = ble.str_to_addr("01DF6947EE77EB")
connection = ble.connect(address, ble.PHY_1M, cb_con, cb_discon)

while connected == False:
    time.sleep_ms(10)

print("Setup client")
gatt_client = ble.GattClient(connection)
print("Discover")
gatt_client.discover()
print("Wait")
time.sleep_ms(1000)

print("Set names")
gatt_client.set_name(UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"), "Notify")

print("Set Callbacks")
gatt_client.set_callback(cb_notify_ind)

print("Show gatt dictionary")
gatt_dict = gatt_client.get_dict()
print(gatt_dict)

print("Enable notify")
gatt_client.subscribe("Notify", True, False)

print("Waiting for notifications")
loop = 0
while loop < 25:
    time.sleep_ms(100)
    loop = loop + 1

print("Disable notify")
gatt_client.subscribe(UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"), False, False)

print("Disconnecting")
connection.disconnect()
while connected == True:
    time.sleep_ms(10)

print("Finished")
del (gatt_client)
del (connection)
