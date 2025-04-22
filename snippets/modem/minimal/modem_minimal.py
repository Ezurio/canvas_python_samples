"""This sample demonstrates how to initialize the modem and wait for it to be ready.
Once the modem is ready it sets the APN, bands, and RAT. These are the minimum settings
a user should set to get the modem on the network.
"""

import canvas_net
import time

initialized = False


def modem_cb(e: tuple):
    """Callback function for modem events."""
    global modem, initialized
    print("Modem event: {}".format(e))
    if e.event == modem.EVENT_STATE:
        if e.data[0] == modem.STATE_INITIALIZED:
            print("Modem initialized successfully")
            initialized = True
        elif e.data[0] == modem.STATE_NOT_READY:
            print("Modem not ready")
            initialized = False


def wait_ready():
    """Wait for the modem to be ready."""
    global initialized
    while not initialized:
        print("Waiting for modem to initialize...")
        time.sleep(2)


modem = canvas_net.Modem(modem_cb)
wait_ready()
# Ensure the correct APN is set to get on the network
print("Setting APN")
modem.set_apn("")
# Ensure the right bands are set to get on the network
print("Setting bands")
modem.set_bands("809189F")
# Ensure the right RAT is set to get on the network
print("Setting RAT")
modem.set_rat(0)
