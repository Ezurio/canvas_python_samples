import canvas_ble as ble
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

def cb_notify(event):
    print("Notify from UUID: ",event.uuid," Name: ", event.name, " Data: ", event.data.decode())

def cb_indicate(event):
    print("Indicate from UUID: ",event.uuid," Name: ", event.name, " Data: ", event.data.decode())
    pass

ble.init()

print("Connecting")
address = ble.str_to_addr("0018C29380052D")
connection = ble.connect(address, ble.PHY_1M, cb_con, cb_discon)

while connected == False:
    time.sleep_ms(10)

print("Discovering")
gatt_client = ble.GattClient(connection)
gatt_client.discover()
time.sleep_ms(1000)

print("Set names")
gatt_client.set_name("b8d00002-6329-ef96-8a4d-55b376d8b25a", "Indicate")

print("Set Callbacks")
gatt_client.set_callbacks(cb_notify, cb_indicate)

print("Enable Indicate")
gatt_client.enable("Indicate", ble.GattClient.CCCD_STATE_INDICATE)

print("Waiting for indications")
loop = 0
while loop < 500:
    time.sleep_ms(100)
    loop = loop + 1

print("Disable Indicate")
gatt_client.enable("Indicate", ble.GattClient.CCCD_STATE_DISABLE)

print("Disconnecting")
connection.disconnect()
while connected == True:
    time.sleep_ms(10)


print("Finished")
del(gatt_client)
del(connection)

