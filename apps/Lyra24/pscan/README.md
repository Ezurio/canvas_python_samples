# Python BLE Scanner
This repository contains Python scripts intended for use on the BL654 USB adapter to provide BLE scanning capbility. This was used with early versions of the [Xbit Desktop tool](https://github.com/LairdCP/Canvas_Xbit_Desktop) access to Bluetooth Low Energy advertisement data.

## Loading onto the BL654 USB Adapter
The BL654 USB adapter must be running [Canvas Firmware](https://github.com/LairdCP/BL654_USB_Adapter_Canvas_Firmware). You can load the Python scripts from this repository as listed below using [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### pscan.py
Rename this file to `main.py` and load onto the BL654 USB adapter.

## Intended Use
Once the BL654 USB adapter has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `pscan.py` to `main.py` so the script runs at boot), the BL654 USB adapter can be used on a workstation in conjunction with versions of [Xbit Desktop](https://github.com/LairdCP/Canvas_Xbit_Desktop) that require pscan.py. 

**Note** As of December 2023, this script is being replaced in newer versions of the Xbit Desktop tool by the `xbit_usb.py` script. Please refer to the README of the corresponding version you installed from the [Xbit Desktop GitHub page](https://github.com/LairdCP/Canvas_Xbit_Desktop) for information about whether the BL654 USB adapter requires `pscan.py` or `xbit_usb.py`.

Xbit Desktop will detect the USB adapter as a serial/COM port and allow you to Connect from within the UI. At this point, Xbit Applets are able to communicate with the BL654 USB adapter to perform Bluetooth scanning and receive scan results from nearby BLE devices.
