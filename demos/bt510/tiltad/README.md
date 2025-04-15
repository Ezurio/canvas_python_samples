# Sentrius BT510 Tilt Sensor Demo
This repository contains Python scripts intended for use on the Sentrius BT510 Sensor for use as a tilt sensor. The accelerometer values are periodically updated and relayed over BLE so external tools can wirelessly detect the angle of tilt of the BT510.

This script is designed for use with the BT510 Tilt Applet available in the [Xbit Desktop tool](https://github.com/Ezurio/Canvas_Xbit_Desktop).

## Loading onto the Sentrius BT510 Sensor
The Sentrius BT510 Sensor must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load the Python scripts from this repository as listed below using [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc). Note that you will need an adapter such as the [USB-SWD Programming Kit](https://www.ezurio.com/wireless-modules/programming-kits/usb-swd-programming-kit) in order to program firmware onto the BT510 and access its UART interface.

### <span>tiltad.py</span>
Rename this file to `main.py` and load onto the Sentrius BT510 sensor.

## Intended Use
Once the Sentrius BT510 Sensor has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `tiltad.py` to `main.py` so the script runs at boot), the Sentrius BT510 Sensor can be used with the BT510 tilt sensor demo available from within [Xbit Desktop](https://github.com/Ezurio/Canvas_Xbit_Desktop) or [Xbit Mobile](https://github.com/Ezurio/Canvas_Xbit_Mobile).
