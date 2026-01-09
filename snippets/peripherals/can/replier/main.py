"""Listens for CAN frames and replies to each frame received by incrementing the CAN ID by 1.
Ctrl-C to exit the monitor_and_reply() loop.
Functions can then be called from the REPL.

Use this sample with another board running ../sender/main.py
"""
import os
import time
from machine import CAN
from machine import Pin
from canvas import Timer


class Replier:
    def __init__(self):
        self.CAN_SEND_TIMEOUT_MS = 100  # Timeout for sending a reply
        self.CAN_RX_BUFFER_SIZE = 256  # Size of the CAN RX buffer
        self.CAN_STATS_INTERVAL_MS = 250  # Interval to print CAN stats
        self.filters = []
        self.sleeping = True
        self.last_stats = None
        self.stats_timer_running = False

        if "bl54l" in os.uname().machine:
            # Set WKP low to avoid excessive current draw on CAN FD 6 click
            wkp = Pin("P1_14", Pin.OUT, 0)
            wkp.off()

        self.stats_timer = Timer(
            self.CAN_STATS_INTERVAL_MS, True, self.stats_timer_callback, None)
        self.can = CAN(CAN.MODE_NORMAL, False,
                       self.can_rx_callback, self.CAN_RX_BUFFER_SIZE)
        self.can_resume()

    def start_stats_timer(self):
        if not self.stats_timer_running:
            self.stats_timer_running = True
            self.stats_timer.start()

    def stop_stats_timer(self):
        self.stats_timer_running = False
        self.stats_timer.stop()

    def can_rx_callback(self, _):
        self.start_stats_timer()

    def stats_timer_callback(self, _):
        stats = self.stats(False)
        if self.last_stats == stats:
            self.stop_stats_timer()
        else:
            print("CAN stats: {}".format(stats))
        self.last_stats = stats

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

    def rx_and_reply(self):
        # Default read timeout is important here to avoid consuming all CPU time
        frame = self.can.read_frame()
        if frame is None:
            return
        id, rtr, data = frame
        try:
            # Increment the CAN ID for the reply to lower the priority and avoid collisions
            self.can.send(id + 1, rtr, data, self.CAN_SEND_TIMEOUT_MS)
        except Exception as e:
            print("Error sending:", e)

    def monitor_and_reply(self):
        print("CAN bus started. Listening for frames...")
        self.can_resume()
        while True:
            self.rx_and_reply()


r = Replier()
r.monitor_and_reply()
