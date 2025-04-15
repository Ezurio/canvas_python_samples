import canvas_ble
import canvas
import binascii

scanner = None
connection = None
timer = None
gatt_client = None
rpc_id = 0
# store a scan rpc id separate so it can be included in scan results
scan_rpc_id = 0

#----------------------------------------------------------------
# Properties
# i: the RPC ID of the request
# e: the error code, if any
# m: the message / method type
# d: the deviceId
# b: hex string of data bytes
# j: JSON object
# r: RSSI 
# t: subtype (for scan results, it's pduType)

#----------------------------------------------------------------
# PUBLIC EXTERNAL FUNCTIONS
# Intended to be called by off-board host applications.
# These functions form xbitLib's external-facing API.

def scannerStopTimerCallback(arg):
    global scanner
    global timer
    scanner.stop()

# Start a BLE scan
def scanStart(active, timeout = 0):
    global scanner
    global rpc_id
    global scan_rpc_id
    global timer
    if scanner != None:
        scan_rpc_id = rpc_id
        try:
            scanner.start(active)
        except:
            print("{'i':" + str(scan_rpc_id) + ",'e':'NOSCAN'}")
            return
        print("{'i':" + str(scan_rpc_id) + "}")
        if timeout != 0:
            timer = canvas.Timer(timeout, False, scannerStopTimerCallback, None)
            timer.start()
    else:
        print("{'i':" + str(scan_rpc_id) + ",'e':'NOSCAN'}")

# Stop a BLE scan
def scanStop():
    global scanner
    global timer
    global rpc_id
    if scanner != None:
        try:
            scanner.stop()
        except:
            print("{'i':" + str(rpc_id) + ",'e':'NOSTOP'}")
            return
        if timer != None:
            timer.stop()
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOSCAN'}")

# Reset/clear filters for BLE scan operation
def scanFilterReset():
    global scanner
    global rpc_id
    if scanner != None:
        try:
            scanner.filter_reset()
        except:
            print("{'i':" + str(rpc_id) + ",'e':'NORESET'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOSCAN'}")

# Add a filter to the BLE scan operation
def scanFilterAdd(filter_type_str, filter_value):
    global scanner
    global rpc_id
    if scanner != None:
        try:
            scanner.filter_add(eval('canvas_ble.Scanner.' + filter_type_str), filter_value)
        except:
            print("{'i':" + str(rpc_id) + ",'e':'EXISTS'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOSCAN'}")

# Connect to a remote BLE device
def bleConnect(addr_str, phy_str):
    global connection
    global rpc_id
    if connection != None:
        # report that we are already connected?
        print("{'i':" + str(rpc_id) + ",'e':'ALREADYCONNECTED'}")
        return
    try:
        connection = canvas_ble.connect(binascii.unhexlify(addr_str), eval('canvas_ble.' + phy_str), con_cb, discon_cb)
    except:
        print("{'i':" + str(rpc_id) + ",'e':'NOCONN'}")
        return
    if connection != None:
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCONN'}")

# Disconnect from a remote BLE device
def bleDisconnect():
    global connection
    global rpc_id
    if connection != None:
        try:
            connection.disconnect()
        except:
            print("{'i':" + str(rpc_id) + ",'e':'NODISC'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCONN'}")

# Get the GATT dictionary
def bleGetGattDictionary():
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            gatt_dict = gatt_client.get_dict()
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'NODICT'}")
            return
        print("{'i':" + str(rpc_id) + ",'j':" + str(gatt_dict) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# Set a friendly name for a GATT characteristic
def bleSetGattName(uuid,char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            gatt_client.set_name(uuid, char_name)
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'EXISTS'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# Enable notification on a GATT characteristic
def bleNotifyEnable(char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            gatt_client.enable(char_name, canvas_ble.GattClient.CCCD_STATE_NOTIFY)
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'EXISTS'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# Disable notification on a GATT characteristic
def bleNotifyDisable(char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            gatt_client.enable(char_name, canvas_ble.GattClient.CCCD_STATE_DISABLE)
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'NOEXIST'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# send a read request over BLE to the requested characteristic ID for the specified connection handle
def bleRead(char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            data = gatt_client.read(char_name)
            print("{'i':" + str(rpc_id) + ",'b':'" + data.hex() + "'}")
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'RERROR'}")
            return
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")
        return

# send a write of 'data' over BLE to the requested characteristic ID for the specified connection handle
def bleWrite(char_name, data):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        try:
            gatt_client.write(char_name, bytes(data))
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'WERROR'}")
            return
        print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

#----------------------------------------------------------------
# PUBLIC INTERNAL FUNCTIONS
# Intended to be called from other Python modules  on this device

# Initialize the xbit library for BLE access
def init():
    canvas_ble.init()
    scan_init()

#----------------------------------------------------------------

# Initialize BLE scanner
def scan_init():
    global scanner
    scanner = canvas_ble.Scanner(scan_cb)
    scanner.set_phys(canvas_ble.PHY_1M)
    scanner.set_timing(100, 100)

# BLE scan result callback
def scan_cb(sr):
    global scan_rpc_id
    sr_obj = {'m':'bleAd','d':binascii.hexlify(sr.addr).decode(),'b':binascii.hexlify(sr.data).decode(),'t':sr.type,'r':sr.rssi,'i':scan_rpc_id}
    print(str(sr_obj).replace(' ',''))

# BLE connection established callback
def con_cb(conn):
    global gatt_client
    global connection
    connection = conn
    gatt_client = canvas_ble.GattClient(connection)
    gatt_client.set_callbacks(notify_cb, indicate_cb)
    gatt_client.discover()
    print("{'m':'bleConnect','d':'" + binascii.hexlify(conn.get_addr()).decode() + "'}")

# BLE disconnect callback
def discon_cb(conn):
    global gatt_client
    global connection
    print("{'m':'bleDisconnect','d':'" + binascii.hexlify(conn.get_addr()).decode() + "'}")
    if gatt_client != None:
        del(gatt_client)
        gatt_client = None
    if connection != None:
        del(connection)
        connection = None

# BLE notification callback
def notify_cb(event):
    # if name is empty, use the uuid instead
    if len(event.name) == 0:
        print("{'m':'bleNotify','n':'" + event.uuid + "','b':'" + event.data.hex() + "'}")
    else:
        print("{'m':'bleNotify','n':'" + event.name + "','b':'" + event.data.hex() + "'}")

# BLE indication callback
def indicate_cb(event):
    print("{'m':'bleIndicate','n':'" + event.name + "','b':'" + event.data.hex() + "'}")
