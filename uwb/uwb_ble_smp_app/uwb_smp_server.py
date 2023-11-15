import pi_smp_server
import uwb_smp_common
import config
import device_db
import zcbor
import uwb_ble_connect

# Our SMP server instance
server = None

# Handler for SMP get IOS UWB command
#
# Request format:
#     { }
#
# Response format:
#     { "blob": <ios_capability_blob> }
#
def smp_get_ios_uwb(req):
    req_obj = zcbor.to_obj(req)
    pass

# Handler for SMP set IOS UWB command
#
# Request format:
#     { "blob": <ios_configuration_blob> }
#
# Response format:
#     { "status": <status> }
#
def smp_set_ios_uwb(req):
    req_obj = zcbor.to_obj(req)
    pass

# Handler for SMP get Android UWB command
#
# Request format:
#     { "device_id": <device_id>,
#       "ble_addr": <ble_addr> }
#
# Response format:
#     { "channel_mask": <channel mask>,
#       "uwb_roles": <uwb roles> }
#
def smp_get_android_uwb(req):
    req_obj = zcbor.to_obj(req)

    db = device_db.lookup_by_device_id(req['device_id']);
    if db == None:
        # This isn't a device we know about
        return None
    print("Received Get Android UWB request from", db.device_id)

    # Claim the BLE connection for this device
    uwb_ble_connect.claim_connection(req['ble_addr'], db)

    # Build the response
    rsp_obj = {}
    rsp_obj['channel_mask'] = (1 << 5) | (1 << 9)
    rsp_obj['uwb_roles'] = config.get_uwb_roles()
    return zcbor.from_obj(rsp_obj, 1)

# Handler for SMP set Android UWB command
#
# Request format:
#     { "device_id": <device_id>,
#       "channel": <channel>,
#       "session_id": <session_id>,
#       "uwb_role": <uwb_role> }
#
# Response format:
#     { "status": <status> }
#
def smp_set_android_uwb(req):
    req_obj = zcbor.to_obj(req)

    db = device_db.lookup_by_device_id(req['device_id']);
    if db == None:
        # This isn't a device we know about
        return None
    print("Received Set Android UWB request from", db.device_id)

    rsp_obj = {}
    if 'session_id' not in req_obj or 'uwb_role' not in req_obj:
        # Missing required fields
        rsp_obj['status'] = -1
    else:
        db.update_smp_info(req_obj['uwb_role'], req_obj['channel'], req_obj['session_id'])
        rsp_obj['status'] = 0
    return zcbor.from_obj(rsp_obj, 1)

# Handler for SMP stop UWB command
#
# Request format:
#     { "device_id": <device_id> }
#
# Response format:
#     { "status": <status> }
#
def smp_stop_uwb(req):
    req_obj = zcbor.to_obj(req)

    db = device_db.lookup_by_device_id(req['device_id']);
    if db == None:
        # This isn't a device we know about
        return None

    # Ask the database to end the UWB session
    db.end_session()

    rsp_obj = { 'status': 0 }
    return zcbor.from_obj(rsp_obj, 1)

# Handler for SMP reset config command
#
# Request format:
#     { }
#
# Response format:
#     { "status": <status> }
#
def smp_reset_config(req):
    # Reset everything
    config.reset()
    device_db.reset()

    # Return a reply
    rsp_obj = { 'status': 0 }
    return zcbor.from_obj(rsp_obj, 1)

# Handler for SMP get device config command
def smp_get_device_config(req):
    req_obj = zcbor.to_obj(req)
    pass

# Handler for SMP set device config command
def smp_set_device_config(req):
    req_obj = zcbor.to_obj(req)
    pass

# Handler for SMP get device db command
def smp_get_device_db(req):
    req_obj = zcbor.to_obj(req)
    pass

# Handler for SMP set device db command
def smp_set_device_db(req):
    req_obj = zcbor.to_obj(req)
    pass

def init():
    global server
    server = pi_smp_server.server(uwb_smp_common.GROUP)
    server.set_handler(uwb_smp_common.READ, uwb_smp_common.CMD_IOS_UWB, smp_get_ios_uwb)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_IOS_UWB, smp_set_ios_uwb)
    server.set_handler(uwb_smp_common.READ, uwb_smp_common.CMD_ANDROID_UWB, smp_get_android_uwb)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_ANDROID_UWB, smp_set_android_uwb)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_STOP_UWB, smp_stop_uwb)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_RESET_CONFIG, smp_reset_config)
    server.set_handler(uwb_smp_common.READ, uwb_smp_common.CMD_DEVICE_CONFIG, smp_get_device_config)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_DEVICE_CONFIG, smp_set_device_config)
    server.set_handler(uwb_smp_common.READ, uwb_smp_common.CMD_DEVICE_DB, smp_get_device_db)
    server.set_handler(uwb_smp_common.WRITE, uwb_smp_common.CMD_DEVICE_DB, smp_set_device_db)
