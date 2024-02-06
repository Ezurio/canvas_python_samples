# UWB Initiator and Responder Sample
This directory contains Python scripts to be used to test UWB ranging between
two Sera NX040 DVK boards.

## Loading onto the Sera NX040 DVK
The Sera NX040 DVK must be running [Canvas Firmware](https://github.com/LairdCP/Sera_NX040_Firmware).
You can load the Python scripts from this repository as listed below using
[Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc).

### sera_nx040_initiator.py
Rename this file to `main.py` and load onto the first Sera NX040 DVK.

### sera_nx040_responder.py
Rename this file to `main.py` and load onto the second Sera NX040 DVK.

## Intended Use
The scripts set up a static configuration for the UWB radio: the first board
is the initator with an address of 0x2222 and the second board is the
responder with an address of 0x3333. A fixed session ID of 0x00000457
is used. A UWB session is started on each board. Once both boards are
powered and running, two-way ranging will start to take place between
the boards. Each board will report the distance (in centimeters) to the
other board. When both boards are not yet running or if they aren't in
range with each other, they will print "No range".

The scripts run in the background, so the board will return to the REPL
prompt as soon as it starts. This permits the user to send Python commands
to the boards as they are running. For example, the scripts define a `start()`
and `stop()` function that starts and stops the UWB ranging session. For
example, once started and ranging, you could type `stop()` on one board to
observe what happens to the other board. The session can be restarted by
typing `start()`.

One note is that the set of function calls within the `start()` function
must be executed in quick succession to avoid the UWB radio going to sleep.
You will likely fail if you attempted to send each line of the `start()`
function to the REPL one at a time.
