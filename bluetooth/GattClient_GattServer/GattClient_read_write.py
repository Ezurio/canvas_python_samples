import canvas_ble as ble
from canvas_ble import UUID
import time

print("GATT Client example\r\n")

connected = False

READ_CHAR = 'ReadChar'
WRITE_CHAR = 'WriteChar'

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
gatt_client.set_name(UUID("b8d00001-6329-ef96-8a4d-55b376d8b25a"), WRITE_CHAR)
gatt_client.set_name(UUID("b8d00004-6329-ef96-8a4d-55b376d8b25a"), READ_CHAR)

print("Show gatt dictionary")
gatt_dict = gatt_client.get_dict()
print(gatt_dict)

print("Write Test")
loop = 0
read_val = bytearray(20)
while loop < 10:
    string = "Client Count: %d" %(loop)
    value = bytes(string,'utf-8')
    print(string)
    gatt_client.write(WRITE_CHAR, value)
    gatt_client.read(READ_CHAR, read_val)
    read_str = read_val.decode('utf-8')
    if read_str != "":
        print("Read value: ", read_str)
    time.sleep_ms(1000)
    loop = loop + 1

print("Disconnecting")
connection.disconnect()
while connected == True:
    time.sleep_ms(100)

print("Finished")
del(gatt_client)
del(connection)

