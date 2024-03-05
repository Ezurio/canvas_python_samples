# Xbit Text Service Gateway Demo Script

This app is intended for use on Canvas
products that support networking (MG100, Pinnacle 100, BL5340 DVK, etc.).
This application provides a demonstration of the capability of these
products to implement a gateway to relay BLE advertisement data to an
MQTT broker.
The app works with peripheral devices running the [XbitTextApp][1]

This application also optionally connects to a LwM2M server for the
purposes of device management.

## Loading onto the device

The following files need to be loaded onto the Canvas device:

    * `main.py` from this directory
    * `config.py` from `modules/general/`
    * `mqtt.py` from `modules/networking/`
    * `sntp.py` from `modules/networking/`
    * `net_helper.py` from `modules/networking/`

All five files should be in the root directory of the Canvas device.

## Configuration

See the top of the main.py file for a description of how to configure
the application.

## Intended Use

Once the device has been configured correctly and connected to the network,
it will start scanning for BLE advertisements from a device running the [XbitTextApp][1]. The advertisement data
is extracted and then periodically sent to the MQTT
broker (e.g., ThingsBoard or AWS IoT).

[1]: ../../bl654_usb/XbitTextApp/XbitTextApp.py "XbitTextApp"
