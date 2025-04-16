"""This sample demonstrates how to use the CAN bus.

Requirements:
- Canvas Python firmrware that supports CAN bus hardware.
  - Supported hardware: BL654 DVK with TCAN4550 connected to SPI bus and relevant IO.
    CS - SIO_16 (gpio 0,16)
    SCK - SIO_41 (gpio 1,9)
    MOSI - SIO_40 (gpio 1,8)
    MISO - SIO_04 (gpio 0,4)
    reset - SIO_15 (gpio 0,15)
    nINT - SIO_34 (gpio 1,2)
"""

import canvas
from machine import CAN

MODE = CAN.MODE_LOOPBACK | CAN.MODE_FD
CAN_MSG_INTERVAL_MS = 5000


def can_cb(frame: tuple):
    print("CAN RX: ", frame)


can = CAN(MODE, True, can_cb)
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
