"""This example will send 1000 messages on boot.
After sending the messages it will put the CAN peripheral to sleep.

send_messages() can be called again to send another 1000 messages.
"""
import os
import time
from machine import CAN
from machine import Pin


class Sender:
    def __init__(self):
        self.SEND_TIMEOUT_MS = 500  # Timeout in milliseconds
        self.SEND_ID = 89218231  # ID for the CAN message
        self.SEND_DATA = b"12345678"  # Data to send
        self.SEND_AMOUNT = 1000  # Number of messages to send
        self.SLEEP_DELAY_MS = 2000  # Delay before sleeping in milliseconds
        self.filters = []
        self.sleeping = True

        if "bl54l" in os.uname().machine:
            # Set WKP low to avoid excessive current draw on CAN FD 6 click
            wkp = Pin("P1_14", Pin.OUT, 0)
            wkp.off()

        self.can = CAN(CAN.MODE_NORMAL, False, self.can_rx_callback)
        self.can_resume()

    def can_rx_callback(self, frame: tuple):
        pass

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
        print("Sending {} messages...".format(self.SEND_AMOUNT))
        start_time = time.ticks_ms()
        while count < self.SEND_AMOUNT:
            try:
                self.can.send(self.SEND_ID, CAN.FRAME_IDE,
                              self.SEND_DATA, self.SEND_TIMEOUT_MS)
            except Exception as e:
                print("Error sending:", e)
            count += 1
        end_time = time.ticks_ms()
        elapsed = time.ticks_diff(end_time, start_time)
        print("Sent in {} ms".format(elapsed))
        print("Wait {} ms before sleep".format(self.SLEEP_DELAY_MS))
        time.sleep_ms(self.SLEEP_DELAY_MS)
        self.can_sleep()
        print("CAN stats: {}".format(self.stats(False)))


s = Sender()
s.send_messages()
