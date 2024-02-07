# LED strip samples
This directory contains Python scripts to demonstrate the use of the LEDStrip
class.

## Loading onto the Sera NX040 DVK
The Sera NX040 DVK must be running [Canvas Firmware](https://github.com/LairdCP/Sera_NX040_Firmware).
You can load the Python scripts from this repository as listed below using
[Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### sera_nx040_led.py
Rename this file to `main.py` and load onto the Sera NX040 DVK. When rebooted, the LED on the
DVK will cycle through various colors on the LED. Ctrl-C can be used on the REPL UART to
interrupt the script.

