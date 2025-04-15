# Xbit USB Adapter
This repository contains Python scripts intended for use on the BL654 USB adapter to provide the [Xbit Desktop tool](https://github.com/Ezurio/Canvas_Xbit_Desktop) access to Bluetooth Low Energy features.

## Loading onto the BL654 USB Adapter
The BL654 USB adapter must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load the Python scripts from this repository as listed below using [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### xbit_usb.py
Rename this file to `main.py` and load onto the BL654 USB adapter.

### xbit_lib.py
Load this file as `xbit_lib.py` onto the BL654 USB adapter. This module is imported by `xbit_usb.py`.

## Intended Use
Once the BL654 USB adapter has been programmed with Canvas Firwmare and the Python scripts in this repository (making sure to rename `xbit_usb.py` to `main.py` so the script runs at boot), the BL654 USB adapter can be used on a workstation in conjunction with [Xbit Desktop](https://github.com/Ezurio/Canvas_Xbit_Desktop).

Xbit Desktop will detect the USB adapter as a serial/COM port and allow you to Connect from within the UI. Once connected, Xbit Applets are able to communicate with the BL654 USB adapter to perform Bluetooth operations for use cases like scanning for and connecting to other BLE-enabled devices and interacting with their BLE services.
