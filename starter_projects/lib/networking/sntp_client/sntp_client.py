import time
import machine
import socket
import select
import struct

class Sntp:
    def __init__(self, host='pool.ntp.org', port=123, timeout=2):
        self.host = host
        self.port = port
        self.timeout = timeout

    def poll(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Send the query
            res = s.sendto(NTP_QUERY, addr)

            # Wait for the response
            s.setblocking(False)
            poller = select.poll()
            poller.register(s, select.POLLIN)
            res = poller.poll(self.timeout * 1000)
            if not res:
                raise Exception("Timeout receiving NTP response")

            # Read the response
            msg = s.recv(48)
        finally:
            s.close()
        val = struct.unpack("!I", msg[40:44])[0]

        # Adjust for 1970 epoch
        val = val - 2208988800

        # Write the value to the RTC
        tm = time.gmtime(val)
        if tm[0] < 2000:
            raise Exception("Invalid year, not setting RTC")
        else:
            machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
