
from net_helper import NetHelper
import socket
import machine


def resolve(address='google.com', port=80):
    """Resolves an address to an IP address

    Args:
        address (str, optional): _description_. Defaults to 'google.com'.
        port (int, optional): _description_. Defaults to 80.
    """
    print("Resolving address for: " + address)
    addr = socket.getaddrinfo(address, port)[0][-1]
    print(addr)


def modem_on():
    net.modem.reset()


def modem_off():
    net.modem.power_off()


# UART0 is on when booted, turn it off
uart0 = machine.UART(0)
uart0.init()
uart0.suspend()

net = NetHelper(None, True)

print("Turn off modem")
modem_off()
