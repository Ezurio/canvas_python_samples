# Xbit Text Service Peripheral Demo Script
This repository contains a set of Python scripts demonstrating an application to enable Canvas BLE devices as a "BLE Peripheral" providing a simple text messaging service. The script offers a `send()` function that can be used both outside of a connection to send text messages in BLE advertisements and also to a BLE central device while in a connection.

This script is designed for use with the BL654 USB adapter and Sera NX040 DVK boards but should be compatible with any BLE-enabled Canvas hardware.

## Loading onto the BL654 USB adapter
The BL654 USB adapter must be running [Canvas Firmware](https://github.com/LairdCP/BL654_USB_Adapter_Canvas_Firmware/releases). Note that you will need to use `nrfutil` to load the Canvas firmware onto the USB adapter following the steps listed at [BL654 USB (451-00004)](https://docs.zephyrproject.org/latest/boards/arm/bl654_usb/doc/bl654_usb.html).

You can then load the Python scripts from this repository as listed below using [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### <span>XbitTextApp.py</span>
Rename this file to `main.py` and load onto the BL654 USB adapter.

### <span>AppBanner.py</span>
Copy this to the BL654 USB adapter. This is a utility class for displaying a startup banner.

### <span>XbitTextService.py</span>
Copy this to the BL654 USB adapter. This class implements the Xbit Text GATT service.

## Intended Use
Running this script on a Canvas BLE-enabled device will enable it to broadcast simple text messages in BLE advertisements and to communicate with 2-way messaging with a connected BLE central device through "message" and "response" characteristics.
