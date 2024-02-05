# SNTP Client Test Script
This repository contains a Python script for testing the Simple Network
Time Protocol (SNTP) client on network-enabled Canvas devices.

## Loading onto a device
The following files need to be loaded onto the Canvas device:

    * main.py from this directory
    * sntp.py from modules/networking/
    * net_helper.py from modules/networking/

All three files should be in the root directory of the Canvas device.

## Operation
The script will wait for the network to come up and then attempt to
set the device's RTC from the network using SNTP. The device's clock
value is printed before and after the attempt so that the user can
verify that SNTP worked.
