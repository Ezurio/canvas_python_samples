import canvas_ble as ble
import time

print("Central connection example\r\n")

def cb_con(conn):
    print("\r\nConnected\r\n")
    #print(conn)
    rssi = conn.get_rssi()
    print("RSSI = ", rssi)

def cb_discon(conn):
    print("\r\nDisconnected\r\n")


ble.init()

address = ble.str_to_addr("0018C29380052D")

connection = ble.connect(address, ble.PHY_1M, cb_con, cb_discon)

count = 0
while count < 30:
    time.sleep_ms(100)
    count += 1
    print(count)

connection.disconnect()

count = 0
while count < 30:
    time.sleep_ms(100)
    count += 1
    print(count)
    
del(connection)
