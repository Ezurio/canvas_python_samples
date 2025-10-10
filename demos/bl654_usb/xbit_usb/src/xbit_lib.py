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
            if filter_type_str == 'FILTER_NAME':
                # for FILTER_NAME, filter_value is a string
                scanner.filter_add(canvas_ble.Scanner.FILTER_NAME, filter_value)
            elif filter_type_str == 'FILTER_UUID':
                # for FILTER_UUID, filter_value is a byte string of 16, 32 or 128 bits
                scanner.filter_add(canvas_ble.Scanner.FILTER_UUID, binascii.unhexlify(filter_value))
            elif filter_type_str == 'FILTER_ADDR':
                # for FILTER_ADDR, filter_value is a byte string of 48 bits
                scanner.filter_add(canvas_ble.Scanner.FILTER_ADDR, binascii.unhexlify(filter_value))
            elif filter_type_str == 'FILTER_MANUF_DATA':
                # for FILTER_MANUF_DATA, filter_value is a byte string of arbitrary length
                scanner.filter_add(canvas_ble.Scanner.FILTER_MANUF_DATA, binascii.unhexlify(filter_value))
            elif filter_type_str == 'FILTER_DATA':
                # for FILTER_DATA, filter_value is a byte string of arbitrary length
                scanner.filter_add(canvas_ble.Scanner.FILTER_DATA, binascii.unhexlify(filter_value))
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
        # Check to see if the gatt_dict dictionary contains a non-string key
        gatt_dict_version = 1
        if getattr(canvas_ble, 'UUID', None) is not None:
            gatt_dict_version = 2
        if gatt_dict_version == 1:
            # For Canvas 1.x, convert the gatt_dict to a string directly
            print("{'i':" + str(rpc_id) + ",'j':" + str(gatt_dict) + "}")
        else:
            # For Canvas 2.x, convert the gatt_dict to a JSON-compatible string
            # iterate through keys and convert any UUID objects to strings
            d = {}
            for key in list(gatt_dict.keys()):
                if isinstance(key, canvas_ble.UUID):
                    service_key = uuidToStr(key)
                    if len(service_key) > 0:
                        d[service_key] = {}
                        for subkey in list(gatt_dict[key].keys()):
                            characteristic_key = uuidToStr(subkey)
                            d[service_key][characteristic_key] = gatt_dict[key][subkey]
            print("{'i':" + str(rpc_id) + ",'j':" + str(d) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# Set a friendly name for a GATT characteristic
def bleSetGattName(uuid,char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        # If canvas_ble has a UUID class, use it to convert char_name to a UUID object
        if getattr(canvas_ble, 'UUID', None) is not None:
            uuid = canvas_ble.UUID(uuid)
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
        # First try Canvas v1.x 'enable' method
        if getattr(gatt_client, 'enable', None) is not None:
            try:
                gatt_client.enable(char_name, canvas_ble.GattClient.CCCD_STATE_NOTIFY)
            except:
                print("{'i':" + str(rpc_id) + ", 'e':'EXISTS'}")
                return
            print("{'i':" + str(rpc_id) + "}")
        else:
            # If that fails, use Canvas v2.x 'subscribe' method
            try:
                if isUuid(char_name):
                    gatt_client.subscribe(canvas_ble.UUID(char_name), True, False)
                else:
                    gatt_client.subscribe(char_name, True, False)
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
        # First try Canvas v1.x 'enable' method
        if getattr(gatt_client, 'enable', None) is not None:
            try:
                gatt_client.enable(char_name, canvas_ble.GattClient.CCCD_STATE_DISABLE)
            except:
                print("{'i':" + str(rpc_id) + ", 'e':'NOEXIST'}")
                return
            print("{'i':" + str(rpc_id) + "}")
        else:
            # If that fails, use Canvas v2.x 'subscribe' method
            try:
                if isUuid(char_name):
                    gatt_client.subscribe(canvas_ble.UUID(char_name), False, False)
                else:
                    gatt_client.subscribe(char_name, False, False)
            except:
                print("{'i':" + str(rpc_id) + ", 'e':'NOEXIST'}")
                return
            print("{'i':" + str(rpc_id) + "}")
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")

# Send a read request over BLE to the requested characteristic ID
def bleRead(char_name):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        # If canvas_ble has a UUID class, use it to convert char_name to a UUID object
        if getattr(canvas_ble, 'UUID', None) is not None:
            char_name = canvas_ble.UUID(char_name)
        try:
            data = gatt_client.read(char_name)
            print("{'i':" + str(rpc_id) + ",'b':'" + data.hex() + "'}")
        except:
            print("{'i':" + str(rpc_id) + ", 'e':'RERROR'}")
            return
    else:
        print("{'i':" + str(rpc_id) + ",'e':'NOCLIENT'}")
        return

# Send a write of 'data' over BLE to the requested characteristic ID
def bleWrite(char_name, data):
    global gatt_client
    global rpc_id
    if gatt_client != None:
        # If canvas_ble has a UUID class, use it to convert char_name to a UUID object
        if getattr(canvas_ble, 'UUID', None) is not None:
            char_name = canvas_ble.UUID(char_name)
            try:
                gatt_client.write(char_name, bytes(data), None)
            except:
                print("{'i':" + str(rpc_id) + ", 'e':'WERROR'}")
                return
            print("{'i':" + str(rpc_id) + "}")
        else:
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
    # First try Canvas v1.x set_callbacks method
    try :
        gatt_client.set_callbacks(notify_cb, indicate_cb)
    except :
        # If that fails, try Canvas v2.x set_callback method
        gatt_client.set_callback(notify_indicate_cb)
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
    # Canvas 1.x firmware includes 'name' attribute in event object
    if hasattr(event, 'name') and event.name is not None:
        # if name is empty, use the uuid instead
        if len(event.name) == 0:
            print("{'m':'bleNotify','n':'" + event.uuid + "','b':'" + event.data.hex() + "'}")
        else:
            print("{'m':'bleNotify','n':'" + event.name + "','b':'" + event.data.hex() + "'}")
    else:
        # Canvas 2.x firmware does not include 'name' attribute in event object
        print("{'m':'bleNotify','n':'" + uuidToStr(event.uuid) + "','b':'" + event.data.hex() + "'}")

# BLE indication callback
def indicate_cb(event):
    print("{'m':'bleIndicate','n':'" + event.name + "','b':'" + event.data.hex() + "'}")

def notify_indicate_cb(event):
    # single callback for both notify and indicate events
    if event.notify:
        notify_cb(event)
    else:
        indicate_cb(event)

# Check if the string contains a UUID in either full or short format
def isUuid(val):
    if str(val)[8] == '-' and str(val)[13] == '-' and str(val)[18] == '-' and str(val)[23] == '-':
        return True
    elif str(val).lower().startswith('0x'):
        return True
    return False

# Convert a UUID object to a string in either full or short format
def uuidToStr(uuid):
    keystr = ''
    if str(uuid).startswith("UUID('") and str(uuid)[14] == '-' and str(uuid)[19] == '-' and str(uuid)[24] == '-' and str(uuid)[29] == '-':
        # full UUID
        keystr = str(uuid).upper()[6:-2]
    elif str(uuid).upper().startswith('UUID(0X'):
        # short UUID
        keystr = '0x' + str(uuid).upper()[7:-1]
    return keystr
