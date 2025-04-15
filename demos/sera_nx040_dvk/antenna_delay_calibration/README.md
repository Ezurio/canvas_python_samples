# UWB Antenna Delay Calibration Update
This repository contains a Python script intended for use on the Sera NX040 DVK
board or Sera NX040 module to update the antenna delay calibration for the UWB
radio. The calibration value in early modules was incorrect and this script can
be used to correct it.

## Loading onto the Sera NX040 DVK
The Sera NX040 DVK must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware).
You can load the Python scripts from this repository as listed below using
[Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### set_antenna_delay_calibration.py
Rename this file to `main.py` and load onto the Sera NX040 DVK.

## Intended Use
This script is intended to be run once on the Sera NX040 DVK or module to
correct the antenna delay calibration value. Once the script is loaded onto
the board, reboot it to automatically run the main.py. The script will
execute quickly. After the script completes, the calibration will be updated
and the script can be replaced by a real application script.

The calibration value does not take effect until the UWB radio is power
cycled.

