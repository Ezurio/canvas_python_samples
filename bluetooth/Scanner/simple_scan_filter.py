import canvas_ble as ble
import time

print("\r\nSimple scan filtering\r\n")
def scan_cb(evt):
    print("Address", evt.addr, "Data", evt.data)
    return 0

filter_string = "Scan Filter Ad"
filter = bytes(filter_string, 'utf-8')

print("Initialise Scanner")
s = ble.Scanner(scan_cb)
s.filter_add(0, filter)

print("start Scanner")
res = s.start(1)

count = 0
while count < 10:
    time.sleep_ms(1000)
    count = count + 1
    print("Loop: ", count)

s.stop()
s.filter_reset()
