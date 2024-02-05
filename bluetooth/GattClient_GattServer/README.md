# GATT Examples.

## Overview.
These examples demonstrate how to setup simple GATT Clients and servers, and how to work with characteristics.
These examples come as convenient pairs of GATTClientXXX.py and GATTServerXXX.py
You will need to alter the BLE address to match your devices.


## Description
### GattClient_read_write.py and GattServer_read_write.py
- Server sets up a simple GATT database with read and write characteristics. Any changes will be displayed via the callback mechanism.
- Client connects to and reads the server and manipulates the characteristics. Any changes will be displayed via the callback mechanism.

### GattClient_notify.py and GattServer_notify.py
- Server sets up a simple GATT database with a notify characteristic. It then waits for the notification to be enabled and starts updating the value.
- Client connects to and reads the server, sets up callbacks and enables the notify. It then waits for a set period of time, displaying any notifications that are received. After the time period has expired it disables the notification and disconnects.

### GattClient_indicate.py and GattServer_indicate.py
- Server sets up a simple GATT database with an indication characteristic. It then waits for the indication to be enabled and starts updating the value. It will also display the reception of an indication acknowledgement.
- Client connects to and reads the server, sets up callbacks and enables the indication. It then waits for a set period of time, displaying any indications that are received. After the time period has expired it disables the indication and disconnects.

### GattClient_write_read_subscribe.py
- Server sets up a database with a writable characteristic and a readable characteristic that can also be subscribed to (notifications or indications).
When the server writes to a characteristic, it will automatically be notified or indicated when enabled.
- The indicate, notify, read, and read_write client examples can be used.

### GattClient_nRF_Connect_tx_power.py and tx_power_server.ncs
- The TX Power example is provided by nRF Connect for desktop and a Nordic DVK. The PC application will automatically load firmware onto the development kit.
- The client connects to advertisements from the server, discovers services, subscribes, and prints data to the terminal.

### GattClient_decrement.py and GattServer_decrement.py
- The client connects to the server and writes a value of 10 to the decrement characteristic.
- When connected, the server decrements its characteristic every second until it is zero.

## Other Requirements
None
