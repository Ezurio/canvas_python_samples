import os
import machine
import time
from canvas_net import Lwm2m
from net_helper import NetHelper
import binascii
import machine

##############################################################################
# Configuration
#
# Fill out the following configuration parameters to match your environment.

bootstrap = 0 # or 1
security_mode = Lwm2m.SECURITY_NOSEC # or Lwm2m.SECURITY_PSK
psk_id = "my-psk-id"
psk = "my-psk"
server_url = "coap://leshan.eclipseprojects.io:5683"
# Endpoint name is a unique identifier for the device.
# Use the device's unique ID to generate a unique endpoint name.
endpoint_name = "my-device_" +  binascii.hexlify(machine.unique_id()).decode()

#
##############################################################################

LWM2M_EVENTS = [
    "NONE",
    "BOOTSTRAP_REG_FAILURE",
    "BOOTSTRAP_REG_COMPLETE",
    "BOOTSTRAP_TRANSFER_COMPLETE",
    "REGISTRATION_FAILURE",
    "REGISTRATION_COMPLETE",
    "REG_TIMEOUT",
    "REG_UPDATE_COMPLETE",
    "DEREGISTER_FAILURE",
    "DISCONNECT",
    "QUEUE_MODE_RX_OFF",
    "ENGINE_SUSPENDED",
    "NETWORK_ERROR",
    "REG_UPDATE",
    "DEREGISTER"
]

lwm2m = None

def reboot_exec_cb(e):
    lwm2m.stop(True)
    print("Rebooting in 2 seconds...")
    time.sleep(2)
    machine.reset()

def event_cb(evt):
    print("LwM2M event: {}".format(LWM2M_EVENTS[evt]))

# Configure the LWM2M client
lwm2m = Lwm2m(event_cb)
lwm2m.set_endpoint_name(endpoint_name)
lwm2m.set((lwm2m.OBJ_SECURITY, 0, 0), server_url)
lwm2m.set((lwm2m.OBJ_SECURITY, 0, 1), bootstrap)
lwm2m.set((lwm2m.OBJ_SECURITY, 0, 2), security_mode)

if security_mode == lwm2m.SECURITY_PSK:
    lwm2m.set((lwm2m.OBJ_SECURITY, 0, 3), psk_id)
    lwm2m.set((lwm2m.OBJ_SECURITY, 0, 5), psk)

if bootstrap == 0:
    lwm2m.set((lwm2m.OBJ_SECURITY, 0, 10), 101)
    lwm2m.create((lwm2m.OBJ_SERVER, 0))
    lwm2m.set((lwm2m.OBJ_SERVER, 0, 0), 101)
    lwm2m.set((lwm2m.OBJ_SERVER, 0, 1), 60)

# Configure the device object
lwm2m.create((lwm2m.OBJ_DEVICE, 0, 0), 32)
lwm2m.set((lwm2m.OBJ_DEVICE, 0, 0), "Laird Connectivity")
lwm2m.create((lwm2m.OBJ_DEVICE, 0, 3), 32)
lwm2m.set((lwm2m.OBJ_DEVICE, 0, 3), os.uname().release)
lwm2m.create((lwm2m.OBJ_DEVICE, 0, 17), 32)
lwm2m.set((lwm2m.OBJ_DEVICE, 0, 17), os.uname().machine)
lwm2m.set_exec_handler((lwm2m.OBJ_DEVICE, 0, 4), reboot_exec_cb)

# Wait for network to come up
print("Waiting for network")
net = NetHelper(None)
net.wait_for_ready()

print("Starting LwM2M wih endpoint name: {}".format(endpoint_name))
# Start the LwM2M client
lwm2m.start(bootstrap != 0)
