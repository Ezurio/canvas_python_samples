# Sera NX040 DVK - UWB Responder Sample
import canvas_uwb

s = None

def range_cb(ranges):
    for r in ranges:
        if r.range < 65535:
            print("address", hex(r.addr), "range is", r.range, "cm")
        else:
            print("No range")

def start():
    global s
    canvas_uwb.init()
    canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))
    s = canvas_uwb.session_new(0x00000457, canvas_uwb.ROLE_RESPONDER)
    s.set_local_addr(0x3333)
    s.set_peer_addr(0x2222)
    s.set_callback(range_cb)
    s.start()

def stop():
    global s
    s.stop()

start()
