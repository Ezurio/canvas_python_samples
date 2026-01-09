"""This sample demonstrates how to use the CAN bus.
It uses loopback mode so a single board can send and receive CAN messages to itself without requiring another CAN device.

Requirements:
- Canvas Python firmrware that supports CAN bus hardware.
"""

import canvas
from machine import CAN

MODE = CAN.MODE_LOOPBACK | CAN.MODE_FD
CAN_MSG_INTERVAL_MS = 5000


def can_cb(_):
    global can
    print("CAN RX: ", can.read_frame())


can = CAN(MODE, True, can_cb)
can.add_filter(0, 0, 0)
can.add_filter(0, 0, CAN.FILTER_IDE)
count = 0


def send_can_msg(data):
    global count
    short_msg = "Hello {}".format(count).encode('utf-8')
    big_msg = "can_fd_msg_{}".format(count).encode('utf-8')
    print("Sending CAN messages")
    # Simple can message
    try:
        can.send(1, 0, short_msg)
    except Exception as e:
        print("Error sending {} [{}]".format(short_msg, e))
    # extended ID message
    try:
        can.send(3000, 1, short_msg)
    except Exception as e:
        print("Error sending {} [{}]".format(short_msg, e))
    # FD message
    try:
        can.send(1, 4, big_msg)
    except Exception as e:
        print("Error sending {} [{}]".format(big_msg, e))
    # FD extended ID message
    try:
        can.send(3000, 5, big_msg)
    except Exception as e:
        print("Error sending {} [{}]".format(big_msg, e))
    count += 1


timer = canvas.Timer(CAN_MSG_INTERVAL_MS, True, send_can_msg, None)
timer.start()
