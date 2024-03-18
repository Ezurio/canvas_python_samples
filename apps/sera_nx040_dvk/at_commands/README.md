# UWB AT Command Application
This directory contains a Python implementation of AT commands for the
Sera NX040. The AT command implementation is limited to UWB functionality,
but can be easily extended to support other operations.

## Loading onto the Sera NX040
The Sera NX040 device must be running [Canvas Firmware](https://github.com/LairdCP/Sera_NX040_Firmware).
You can load the Python scripts from this repository as listed below using
[Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

The following files need to be loaded onto the device:

    * at_string.py from modules/at_commands
    * at_reader.py from modules/at_commands
    * at_handler.py and main.py from this directory

All four files should be loaded into the root directory of the device.

## Intended Use
Once the Sera NX040 has been programmed with Canvas Firmware and the Python
script in this repository, the AT commands can be used over the REPL UART to
control the UWB radio. The currently supported commands are documented
[here](at_commands.rst).

The script supports two methods of bypassing the AT command handler. Pressing
the user button on the DVK during boot will not start AT command handling and
immediately return to the Python REPL. Additionally, when the AT command handler
is running, sending a Ctrl-C will also return to the board the the REPL.
