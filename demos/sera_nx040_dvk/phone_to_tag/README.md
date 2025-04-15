# UWB Phone to Tag Application
This repository contains a Python script intended for use on the Sera NX040 DVK
board to provide a demonstration of the UWB ranging capabilities between a
mobile phone and the DVK.

## Loading onto the Sera NX040 DVK
The Sera NX040 DVK must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware).
You can load the Python scripts from this repository as listed below using
[Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### phone_to_tag.py
Load the `phone_to_tag.py` file onto the Sera NX040 DVK and rename it `main.py`.

## Intended Use
Once the Sera NX040 DVK has been programmed with Canvas Firmware and the Python
script in this repository, the DVK can be used in conjunction with a TBD mobile
app for iOS and Android to demonstrate UWB ranging between the phone and the
DVK.
