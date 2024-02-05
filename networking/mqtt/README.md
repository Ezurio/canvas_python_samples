# MQTT Client Test Script
This repository contains a Python script for testing the MQTT
client on network-enabled Canvas devices.

## Loading onto a device
The following files need to be loaded onto the Canvas device:

    * mqtt.py from modules/networking/
    * net_helper.py from modules/networking/

One of the two main_*.py files from this directory also need to be
loaded on to the device. Rename the chosen file so that it appears
as main.py on the device.

There is a configuration section near the top of the main.py file
that needs to be modified with the correct parameters for your
MQTT broker.

All three files should be in the root directory of the Canvas device.

## Operation
The script will wait for the network to come up and then attempt to
connect to the MQTT broker and publish a single message.
