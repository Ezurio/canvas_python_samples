# GattClient / GattServer Examples.

## Overview.
These examples demonstrate how to setup simple GATT clients and servers, and how to work with characteristics.
These examples come as convenient pairs of GattClientXXX.py and GattServerXXX.py
You will need to alter the BLE address to match your devices.


## Description
### GattClient_read_write.py and GattServer_read_write.py
- Server sets up a simple GATT database with read and write characteristics. Any changes will be displayed via the callback mechanism.
- Client connects to and reads the server and manipulates the characteristics. Any changes will be displayed via the callback mechanism.

### GattClient_notify.py and GattServer_notify.py
- Server sets up a simple GATT database with a notify characteristic. It then waits for the notification to be enabled and starts updating the value.
- Client connects to and reads the server, sets up callbacks and enables the notify. It then waits for a set period of time, diplaying any notifications that are received. After the time period has expired it disables the notification and disconnects.

### GattClient_indicate.py and GattServer_indicate.py
- Server sets up a simple GATT database with an indication characteristic. It then waits for the indication to be enabled and starts updating the value. It will also display the reception of an indication acknowledgement.
- Client connects to and reads the server, sets up callbacks and enables the indication. It then waits for a set period of time, diplaying any indications that are received. After the time period has expired it disables the indication and disconnects.


## Other Requirements
None
