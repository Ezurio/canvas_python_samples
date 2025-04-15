import canvas_uwb

# MULTI_NODE_MODE definitions
ANCHOR_MODE_UNICAST=b'\x00'
ANCHOR_MODE_MULTICAST=b'\x01'

class Anchor:

    def __init__(self, config, led):
        self.config = config
        self.led = led
        self.local_addr = self.config.config['local_addr']
        self.session_id = self.config.config['session_id']
        self.session_id_str = hex(self.session_id)[2:]
        self.session = None

        # Devices dictionary format:
        #  key: full device ID string (8 bytes, 16 characters)
        #  value: dictionary with the following fields:
        #     session_id: session ID
        #     short_addr: short address
        #     range: range result
        self.devices = {}
        self.role = canvas_uwb.ROLE_INITIATOR
        self.mode = ANCHOR_MODE_MULTICAST

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

        # Update the advertisement data
        #ad_update(False)

        # Set LED back to base color
        color = self.config.config['base_led']
        self.led.set(color)

    def start(self):
        # Check if session already started
        if self.session != None:
            print("Session already started")
            return

        # Check for peer list in config
        peer_addr_list = self.config.config['peer_addr_list']
        if len(peer_addr_list) == 0:
            print("No peer addresses, add tag short addresses to peer list in config before starting a session")
            return
        
        # Create the session
        print("Starting multicast session", self.session_id_str, "with interval", self.config.config['ranging_interval_ms'], "ms")
        self.session = canvas_uwb.session_new(self.session_id, self.role)
        self.session.set_local_addr(self.local_addr)
        self.session.set_peer_addr(peer_addr_list[0]) # add first peer address
        self.session.set_callback(self.range_cb)
        self.session.set_app_config(0x03, self.mode)

        # Set the slot duration and ranging interval
        self.session.set_app_config(canvas_uwb.CONFIG_SLOT_DURATION, (self.config.config['slot_duration_ms']*1200).to_bytes(2,'little'))
        self.session.set_app_config(canvas_uwb.CONFIG_SLOTS_PER_RR, (self.config.config['slots_per_rr']).to_bytes(1,'little'))
        self.session.set_ranging_interval(self.config.config['ranging_interval_ms'])

        # Start the session
        err = self.session.start()
        if err == False:
            print("Session start failed")
            return
        
        # Add additional peer addresses
        if len(peer_addr_list) > 1:
            for i in range(1, len(peer_addr_list)):
                self.session.add_multicast(peer_addr_list[i])

        # Create a new device record for each peer device
        for peer_device_addr in peer_addr_list:
            d = {}
            d['session_id'] = self.session_id
            d['short_addr'] = peer_device_addr
            d['range'] = 65535
            self.devices[str(hex(peer_device_addr))[2:]] = d
            

    def stop(self):
        print("Stopping session", hex(self.session_id)[2:])

        # Find the session
        if self.session != None:
            self.session.stop()
            self.session.close()
            self.session = None

        # Remove sessions's devices from the devices dictionary
        to_remove = []
        for d in self.devices:
            if self.devices[d]['session_id'] == self.session_id:
                to_remove.append(d)
        for d in to_remove:
            del self.devices[d]
        pass
