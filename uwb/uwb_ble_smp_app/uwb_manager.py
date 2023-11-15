import config
import device_db
import pi_uwb

# Number of active ranging sessions
num_sessions = 0

# Defines the next session ID that we will use
next_session_id = 0

class Session:
    def __init__(self, peer:device_db.Device, peer_role:int, session_id:int):
        self.peer_db = peer
        self.peer_addr = peer.short_addr()
        self.peer_role = peer_role
        self.session_id = session_id
        self.active = False

        print("Session: Start ranging with", self.peer_db.device_id)

        # If ranging is not already active, start up the radio
        if num_sessions == 0:
            pi_uwb.init()
            pi_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))

        # Start our new session
        if self.peer_role == config.UWB_ROLE_RESPONDER:
            self.session = pi_uwb.session_new(self.session_id, pi_uwb.PI_UWB_ROLE_INITIATOR)
        else:
            self.session = pi_uwb.session_new(self.session_id, pi_uwb.PI_UWB_ROLE_RESPONDER)
        self.session.set_local_addr(config.short_addr())
        self.session.set_peer_addr(self.peer_addr)
        self.session.set_callback(self.range_cb)
        self.session.start()
        num_sessions += 1
        if num_sessions == 1:
            config.set_ranging_active(True)

    def __del__(self):
        if self.session is not None:
            self.session.stop()
            self.session = None
            num_sessions -= 1
            if num_sessions == 0:
                config.set_ranging_active(False)

    def range_cb(self, evt):
        print("Session: Range to", self.peer_db.device_id, "is", evt.range)
        if evt.range < 65535:
            self.range = evt.range
        else:
            self.range = None

def next_session_id() -> int:
    global next_session_id
    next_session_id += 1
    return next_session_id
