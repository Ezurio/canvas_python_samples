import config
import device_db
import uwb_ble_connect
import uwb_smp_common
import pi_smp_client
import pi_ble_common
import zcbor
import sync

# State definitions
STATE_GET_CAPABILITIES = 0
STATE_SET_CONFIG = 1
STATE_ACTIVE = 2

# Connections that need attention
pending_devices = []

class SMPClient:
    def __init__(self, db: device_db.Device, conn: uwb_ble_connect.Connection):
        self.db = db
        self.client = None
        self.conn = conn
        self.state = STATE_GET_CAPABILITIES

        # Create an SMP client
        print("Creating SMP client")
        self.client = pi_smp_client.client(conn.conn)

        # Close the connection if we couldn't create the client
        if self.client is None:
            self.conn.disconnect()

        # Put the client in the pending list
        pending_devices.append(self)

        # Wake up the main loop to process this device
        sync.signal()

def service_one():
    if len(pending_devices) == 0:
        # No pending devices
        return

    # Get the next pending device
    self = pending_devices.pop(0)

    # Build the next request depending on the current state
    if self.state == STATE_GET_CAPABILITIES:
        print("Sending Get Android UWB request to", self.db.device_id)
        # Send the request
        req_obj = {}
        req_obj['device_id'] = config.device_id_str()
        req_obj['ble_addr'] = pi_ble_common.my_addr()
        rsp = self.client.send(uwb_smp_common.READ, uwb_smp_common.GROUP,
                uwb_smp_common.CMD_ANDROID_UWB, zcbor.from_obj(req_obj, 0))
        if rsp is None:
            # Failed to send the request
            self.conn.disconnect()
            return

        # Convert response from CBOR
        rsp_obj = zcbor.to_obj(rsp)
        if rsp_obj is None:
            # Failed to parse the response
            self.conn.disconnect()
            return

        # Check for the expected response
        if 'uwb_roles' in rsp_obj and 'channel_mask' in rsp_obj:
            # Pass the data back to the database
            self.db.update_smp_info(rsp_obj['uwb_roles'], rsp_obj['channel_mask'])
        else:
            # This is an invalid response
            self.conn.disconnect()
            return

        # Move to the next state
        self.state = STATE_SET_CONFIG
        pending_devices.append(self)
    elif self.state == STATE_SET_CONFIG:
        # Get the parameters we'll need to send
        session_id, peer_role = self.db.get_session_info()

        # Convert from peer role to my role
        if peer_role == config.UWB_ROLE_INITIATOR:
            my_role = config.UWB_ROLE_RESPONDER
        else:
            my_role = config.UWB_ROLE_INITIATOR

        # Build the request
        req_obj = {}
        req_obj['device_id'] = config.device_id_str()
        req_obj['channel'] = 0
        req_obj['session_id'] = session_id
        req_obj['uwb_role'] = my_role

        # Send the request
        print("Sending Set Android UWB request to", self.db.device_id)
        rsp = self.client.send(uwb_smp_common.WRITE, uwb_smp_common.GROUP,
                uwb_smp_common.CMD_ANDROID_UWB, zcbor.from_obj(req_obj, 0))
        if rsp is None:
            # Failed to send the request
            self.conn.disconnect()
            return

        # Convert response from CBOR
        rsp_obj = zcbor.to_obj(rsp)
        if rsp_obj is None:
            # Failed to parse the response
            self.conn.disconnect()
            return

        # Check for the expected response
        if 'status' not in rsp_obj:
            # This is an invalid response
            self.conn.disconnect()
            return
        elif rsp_obj['status'] != 0:
            # The request failed
            self.conn.disconnect()
            return

        # Move to the next state
        self.state = STATE_ACTIVE
    elif self.state == STATE_ACTIVE:
        # Nothing to do
        pass
    else:
        # This is an invalid state
        self.conn.disconnect()
        pass

    if len(pending_devices) > 0:
        # Wake up the main loop again
        sync.signal()
