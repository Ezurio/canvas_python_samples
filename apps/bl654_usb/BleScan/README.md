# BLE Scanning and Connection Demo
This repository contains a simple Python script demonstrating scanning for peripherals advertising a specific GATT service UUID, establishing a connection and writing to a characteristic.

This script is designed for use with the BL654 USB adapter and Sera NX040 DVK boards but should be compatible with any BLE-enabled Canvas hardware.

## Loading onto the BL654 USB adapter
The BL654 USB adapter must be running [Canvas Firmware](https://github.com/LairdCP/BL654_USB_Adapter_Canvas_Firmware/releases). Note that you will need to use `nrfutil` to load the Canvas firmware onto the USB adapter following the steps listed at [BL654 USB (451-00004)](https://docs.zephyrproject.org/latest/boards/arm/bl654_usb/doc/bl654_usb.html).

You can then load the Python scripts from this repository as listed below using [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc). 

### <span>BleScan.py</span>
Rename this file to `main.py` and load onto the BL654 USB adapter.

## Intended Use
This script scans for nearby BLE peripherals advertising a specific GATT service UUID. When running, if a peripheral is found, this script will initiate a BLE connection, discover services and write a string to a specific characteristic to demonstrate basic BLE central operation.
