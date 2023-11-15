import time
import canvas_ble as ble

print("\r\nSimple Scan Example\r\n")

def scan_cb(evt):
    address = ble.addr_to_str(evt.addr)
    print("Address", address, "Data", evt.data)
    return 0

ble.init()
s = ble.Scanner(scan_cb)
res = s.start(1)

count = 0
while count < 10:
    time.sleep_ms(1000)
    count = count + 1
    print("Loop: ", count)

s.stop()



