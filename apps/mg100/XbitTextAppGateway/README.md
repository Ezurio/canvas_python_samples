# BLE-to-MQTT application
This repository contains a Python application intended for use on Canvas
products that support networking (MG100, Pinnacle 100, BL5340 DVK, etc.).
This application provides a demonstration of the capability of these
products to implement a gateway to relay BLE advertisement data to an
MQTT broker.

This application also optionally connects to a LwM2M server for the
purposes of device management.

## Loading onto the device
The following files need to be loaded onto the Canvas device:

    * main.py from this directory
    * config.py from this directory
    * mqtt.py from modules/networking/
    * sntp.py from modules/networking/
    * net_helper.py from modules/networking/

All five files should be in the root directory of the Canvas device.

## Configuration
See the top of the main.py file for a description of how to configure
the application.

## Intended Use
Once the device has been configured correctly and connected to the network,
it will start scanning for BLE advertisements from a Laird Connectivity BT510
that is advertising sensor data. The sensor data, specifically temperature,
is extracted from the advertisement and then periodically sent to the MQTT
broker (e.g., ThingsBoard or AWS IoT).
