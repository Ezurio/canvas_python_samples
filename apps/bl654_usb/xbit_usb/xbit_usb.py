app_id='xbit_usb'
app_ver='0.1.0'

import sys
import xbit_lib

# -----------------------------------------------------------
# JSON Command Examples, corresponding to xbit_lib.* API calls
# -----------------------------------------------------------
# def scanStart(active)
# example of calling 'scanStart(0)':
# {'x':'scanStart(1,5)','i':1}

# def scanStop()
# example of calling 'scanStop()':
# {'x':'scanStop()','i':2}

# def scanFilterReset()
# example of calling 'scanFilterReset()':
# {'x':'scanFilterReset()','i':3}

# def scanFilterAdd(filter_type_str, filter_value)
# example of calling "scanFilterAdd('FILTER_NAME', 'BT510-77')"
# {'x':'scanFilterAdd("FILTER_NAME", "BT510-77")','i':4}

# def bleConnect(addr_str, phy_str)
# example of calling "bleConnect('01774e7537efd4', 'PHY_1M')"
# {'x':'bleConnect("01774e7537efd4","PHY_1M")','i':5}

# def bleDisconnect()
# example of calling 'bleDisconnect()'
# {'x':'bleDisconnect()','i':6}

# def bleGetGattDictionary()
# example of calling 'bleGetGattDictionary()'
# {'x':'bleGetGattDictionary()','i':7}

# def bleSetGattName(uuid,char_name)
# example of calling "bleSetGattName('da2e7828-fbce-4e01-ae9e-261174997c48','smp')"
# {'x':'bleSetGattName("da2e7828-fbce-4e01-ae9e-261174997c48","smp")','i':8}

# def bleNotifyEnable(char_name)
# example of calling 'bleNotifyEnable("smp")'
# {'x':'bleNotifyEnable("smp")','i':9}

# def bleNotifyDisable(char_name)
# example of calling 'bleNotifyDisable("smp")'
# {'x':'bleNotifyDisable("smp")','i':10}

# def bleWrite(char_name, data)
# example of calling 'bleWrite()':
# {'x':'bleWrite("smp",[0x02, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00, 0xBF, 0x61, 0x64, 0x65, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0xFF])','i':11}
#
# The above bleWrite() sends an SMP echo command with the text 'Hello'
# The device should respond with a notification containing the bytes
# described below:
#
# |---------SMP---------|-----------CBOR-------------|
# |-> MGMT_OP_WRITE_RSP (3)
# |  |-> Flags (TBD)
# |  |  |-> Len (10 bytes)
# |  |  |     |-> Group (0x0000 is MGMT_GROUP_ID_OS)
# |  |  |     |     |-> Seq (0x00)
# |  |  |     |     |  |-> Command Id (0x00 is OS_MGMT_ID_ECHO)
# |  |  |     |     |  |
# |  |  |     |     |  |  |-> # map(*)
# |  |  |     |     |  |  |  |-> # text(1)
# |  |  |     |     |  |  |  |  |-> # "r"
# |  |  |     |     |  |  |  |  |  |-> # text(5)
# |  |  |     |     |  |  |  |  |  |  |-> # "Hello"
# |  |  |     |     |  |  |  |  |  |  |              |-> # primitive(*)  
# 03 00 00 0a 00 00 00 00 bf 61 72 65 48 65 6c 6c 6f ff
# start the xbit shell to receive commands
def xbitShellStart():
    # loop forever waiting for input from xbit
    while True:
        print('xbit>',end="")
        try:
            cmd = sys.stdin.readline()
        except:
            print("")
            break
        processCmd(cmd.strip())

# process a JSON command
def processCmd(json_cmd):
    if(len(json_cmd) == 0):
        return
    if(type(json_cmd) != str):
        return
    if(json_cmd[0] != '{'):
        return
    if(json_cmd[-1] != '}'):
        return
    # convert JSON command to a dictionary
    try:
        cmd = eval(json_cmd)
        xbit_lib.rpc_id = cmd['i']
        eval('xbit_lib.' + cmd['x'])
    except (Exception):
        pass

# initialize the xbit library
xbit_lib.init()
