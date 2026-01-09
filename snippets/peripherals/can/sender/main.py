"""This example will send 1000 messages on boot.
After sending the messages it will put the CAN peripheral to sleep.

s.send_messages() can be called again to send another 1000 messages.
"""
import os
import time
from machine import CAN
from machine import Pin
from canvas import Timer


class Sender:
    def __init__(self):
        self.SEND_TIMEOUT_MS = 100  # Timeout in milliseconds
        self.SEND_ID = 89218231  # ID for the CAN message
        self.SEND_DATA = b"12345678"  # Data to send
        self.SEND_AMOUNT = 1000  # Number of messages to send
        self.SLEEP_DELAY_MS = 2000  # Delay before sleeping in milliseconds
        self.INTERFRAME_DELAY_US = 600  # Delay between messages when sending in loop
        self.CAN_RX_BUFFER_SIZE = 256  # Size of the CAN RX buffer
        self.CAN_STATS_TIMER_MS = 250  # Interval to print CAN stats
        self.filters = []
        self.sleeping = True
        self.last_stats = None
        self.stats_timer_running = False

        if "bl54l" in os.uname().machine:
            # Set WKP low to avoid excessive current draw on CAN FD 6 click
            wkp = Pin("P1_14", Pin.OUT, 0)
            wkp.off()

        self.stats_timer = Timer(
            self.CAN_STATS_TIMER_MS, True, self.stats_timer_callback, None)
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
        self.can.clear_rx_queue()
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

    def send_messages(self):
        self.can_resume()
        count = 0
        self.stats_timer.start()
        print("Sending {} messages...".format(self.SEND_AMOUNT))
        start_time = time.ticks_ms()
        while count < self.SEND_AMOUNT:
            try:
                self.can.send(self.SEND_ID, CAN.FRAME_IDE,
                              self.SEND_DATA, self.SEND_TIMEOUT_MS)
            except Exception as e:
                print("Error sending:", e)
            time.sleep_us(self.INTERFRAME_DELAY_US)
            count += 1
        end_time = time.ticks_ms()
        elapsed = time.ticks_diff(end_time, start_time)
        print("Sent in {} ms".format(elapsed))
        print("Wait {} ms before sleep".format(self.SLEEP_DELAY_MS))
        time.sleep_ms(self.SLEEP_DELAY_MS)
        self.can_sleep()


s = Sender()
s.send_messages()
