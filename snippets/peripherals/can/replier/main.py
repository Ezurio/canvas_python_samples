"""Listens for CAN frames and replies to each frame received by incrementing the CAN ID by 1.
Ctrl-C to exit the monitor_and_reply() loop.
Functions can then be called from the REPL.

Use this sample with another board running ../sender/main.py
"""
import os
import time
from machine import CAN
from machine import Pin


class Replier:
    def __init__(self):
        self.REPLY_INTERVAL_MS = 100  # Interval to send replies
        self.REPLY_TIMEOUT_MS = 500  # Timeout for sending a reply
        self.filters = []
        self.sleeping = True
        self.can_queue = []

        if "bl54l" in os.uname().machine:
            # Set WKP low to avoid excessive current draw on CAN FD 6 click
            wkp = Pin("P1_14", Pin.OUT, 0)
            wkp.off()

        self.can = CAN(CAN.MODE_NORMAL, False, self.can_rx_callback)
        self.can_resume()

    def can_rx_callback(self, frame: tuple):
        try:
            self.can_queue.append(frame)
        except Exception as e:
            print("Error appending frame to queue:", e)

    def can_sleep(self):
        for f in self.filters:
            self.can.remove_filter(f)
        self.filters.clear()
        self.can.stop()
        self.can.suspend()
        self.sleeping = True
        print("CAN in sleep mode")

    def can_resume(self):
        if not self.sleeping:
            return
        try:
            self.can.resume()
        except:
            pass
        # Accept all frames
        self.filters.append(self.can.add_filter(0, 0, 0))
        self.filters.append(self.can.add_filter(0, 0, CAN.FILTER_IDE))
        self.can.set_bitrate(250000)
        self.can.start()
        self.sleeping = False

    def restart_can(self):
        if self.sleeping:
            return
        self.can.stop()
        self.can.start()

    def clear_stats(self):
        self.can.get_stats(True)

    def stats(self, print_stats=True):
        stats = self.can.get_stats()
        if print_stats:
            print(stats)
        return stats

    def send_reply(self):
        if (len(self.can_queue) == 0):
            return
        print("Can queue length:", len(self.can_queue))
        while len(self.can_queue) > 0:
            frame = self.can_queue.pop(0)
            can_id, rtr, data = frame
            try:
                # Increment the CAN ID for the reply to lower the priority and avoid collisions
                self.can.send(can_id + 1, rtr, data, self.REPLY_TIMEOUT_MS)
            except Exception as e:
                print("Error sending:", e)
        self.stats()

    def monitor_and_reply(self):
        self.can_resume()
        while True:
            self.send_reply()
            time.sleep_ms(self.REPLY_INTERVAL_MS)


print("CAN bus started. Listening for frames...")
r = Replier()
r.monitor_and_reply()
