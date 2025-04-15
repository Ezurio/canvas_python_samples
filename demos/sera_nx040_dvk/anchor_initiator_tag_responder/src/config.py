import machine
import canvas

SESSION_ID_OFFSET = 0x12340000
DEFAULT_RANGING_INTERVAL_MS = 1000
DEFAULT_ADVERTISING_INTERVAL_MS = 100

class Config:
    def __init__(self):
        self.config = {}
        self.load()

    def load(self):
        self.config = {}
        self.config['ble_name'] = "UWB Simple"
        self.config['base_led'] = 0x000f00
        self.config['error_led'] = 0x000000
        self.config['range_led'] = 0x003f00
        self.config['network_id'] = 0
        self.config['anchor_mode'] = 0
        self.config['peer_addr_list'] = []
        self.config['session_id_list'] = []
        self.config['ranging_interval_ms'] = DEFAULT_RANGING_INTERVAL_MS
        self.config['advertising_interval_ms'] = DEFAULT_ADVERTISING_INTERVAL_MS
        self.config['slot_duration_ms'] = 2
        self.config['slots_per_rr'] = 25

        # Get our short address
        self.config['dev_id'] = machine.unique_id()
        self.config['local_addr'] = (int(self.config['dev_id'][1]) << 8) | int(self.config['dev_id'][0])
        self.config['session_id'] = self.config['local_addr'] + SESSION_ID_OFFSET

        try:
            f = open('config.cb', 'rb')
        except:
            print("Config file not found")
            return

        cbor = f.read()
        f.close()
        if cbor is None:
            return

        config_file = canvas.zcbor_to_obj(cbor)
        if config_file is None:
            self.save() # save defaults if no file exists
            return

        for c in config_file:
            self.config[c] = config_file[c]

    def save(self):
        cbor = canvas.zcbor_from_obj(self.config, 0)
        if cbor is None:
            return

        f = open("config.cb", "wb")
        if f is None:
            return

        size = f.write(cbor)
        f.close()
