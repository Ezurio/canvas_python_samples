import canvas
import canvas_uwb
import time

# MULTI_NODE_MODE definitions
TAG_MODE_UNICAST=b'\x00'
TAG_MODE_MULTICAST=b'\x01'

class Tag:

    def __init__(self, config, led):
        self.config = config
        self.led = led
        self.local_addr = self.config.config['local_addr']
        self.session_id_list = self.config.config['session_id_list']
        self.sessions = {}
        self.role = canvas_uwb.ROLE_RESPONDER
        self.mode = TAG_MODE_MULTICAST
        self.devices = {}

        # Initialize the radio
        canvas_uwb.init()

        # Disable the current limiter, assume we're on a big battery
        result = canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))


    def range_cb(self, ranges):
        # Update the LED
        color = self.config.config['range_led']
        for r in ranges:
            if r.range == 65535:
                color = self.config.config['error_led']
                break
        self.led.set(color)

        for r in ranges:
            # Find a matching device in the devices dictionary
            dev_id_str = None
            for d in self.devices:
                if self.devices[d]['short_addr'] == r.addr:
                    dev_id_str = d
                    break

            # If found a matching device, update its range
            if dev_id_str is not None:
                self.devices[dev_id_str]['range'] = r.range
                self.devices[dev_id_str]['timestamp_delta'] = time.ticks_ms() - self.devices[dev_id_str]['last_timestamp']
                self.devices[dev_id_str]['last_timestamp'] = time.ticks_ms()

        # Update the advertisement data
        #ad_update(False)

        # Set LED back to base color
        color = self.config.config['base_led']
        self.led.set(color)
    
    def start(self):
        # Check for peer list in config
        session_id_list = self.config.config['session_id_list']
        if len(session_id_list) == 0:
            print("No sessions, add anchor session IDs to config before starting a session")
            return

        for session_id in self.session_id_list:
            # check if a session already started, don't start it again
            if hex(session_id)[2:] in self.sessions:
                print("Session",hex(session_id)[2:],"already started, skipping")
                continue

            # Create the session
            session = canvas_uwb.session_new(session_id, self.role)
            session.set_local_addr(self.local_addr)
            peer_addr = session_id & 0xFFFF # Lower 16 bits of session ID is the peer (anchor) address for this session
            session.set_peer_addr(peer_addr)
            session.set_callback(self.range_cb)
            session.set_app_config(0x03, self.mode)
            session.set_app_config(canvas_uwb.CONFIG_SLOT_DURATION, (self.config.config['slot_duration_ms']*1200).to_bytes(2,'little'))
            session.set_app_config(canvas_uwb.CONFIG_SLOTS_PER_RR, (self.config.config['slots_per_rr']).to_bytes(1,'little'))
            session.set_ranging_interval(self.config.config['ranging_interval_ms'])

            # Start the session
            err = session.start()
            if err == False:
                print("Session start failed")
                return

            # Create a new session record
            s = {}
            s['session'] = session
            s['mode'] = self.mode
            s['devices'] = [ peer_addr ]
            self.sessions[hex(session_id)[2:]] = s

            # Create a new device record for each peer device
            d = {}
            d['session_id'] = session_id
            d['short_addr'] = peer_addr
            d['range'] = 65535
            d['last_timestamp'] = 0
            d['timestamp_delta'] = 0
            self.devices[str(hex(peer_addr))[2:]] = d


    def stop(self):
        for session_id in self.session_id_list:
            print("Stopping session", hex(session_id)[2:])
            session = self.sessions[hex(session_id)[2:]]
            if session['session'] is not None:
                session['session'].stop()
                session['session'] = None
            del self.sessions[hex(session_id)[2:]]
