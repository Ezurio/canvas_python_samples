import canvas_ble as ble
from canvas_ble import UUID
import time

print("GATT Client Indicate example\r\n")

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

print("Discovering")
gatt_client = ble.GattClient(connection)
gatt_client.discover()
time.sleep_ms(1000)

print("Set names")
gatt_client.set_name(UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"), "Indicate")

print("Set Callbacks")
gatt_client.set_callback(cb_notify_ind)

print("Enable Indicate")
gatt_client.subscribe("Indicate", False, True)

print("Waiting for indications")
loop = 0
while loop < 500:
    time.sleep_ms(100)
    loop = loop + 1

print("Disable Indicate")
gatt_client.subscribe("Indicate", False, False)

print("Disconnecting")
connection.disconnect()
while connected == True:
    time.sleep_ms(10)


print("Finished")
del (gatt_client)
del (connection)
