import time
import network
import canvas

# How often to check for network state
PERIODIC_TIMER = 5000 # 5 seconds

# How long to wait for the modem to be ready
MODEM_READY_LIMIT = 9000 # 15 minutes

# How long to wait for the network to be ready
NETWORK_READY_LIMIT = 200 # 20 seconds

class NetHelper:
    def modem_cb(self, e: tuple):
        if self.verbose:
            print("Modem Event: {}".format(e))

        # Save initial state
        was_net_ready = self.net_ready

        # Check for state change
        if e.event == self.modem.EVENT_STATE:
            if e.data[0] == self.modem.STATE_INITIALIZED:
                self.modem_ready = True
                if self.nic.isconnected():
                    self.net_ready = True
            else:
                self.modem_ready = False
                self.net_ready = False

        # Call callback if something changed
        if was_net_ready != self.net_ready:
            if self.verbose:
                print("Network Ready: {}".format(self.net_ready))
            if self.callback is not None:
                self.callback(self.net_ready)

    def periodic_cb(self, data):
        # Save initial state
        was_net_ready = self.net_ready

        # Check for state change
        if self.modem_ready == True:
            if self.nic.isconnected() == False:
                self.net_ready = False
            else:
                self.net_ready = True

        # Call callback if something changed
        if was_net_ready != self.net_ready:
            if self.verbose:
                print("Network Ready: {}".format(self.net_ready))
            if self.callback is not None:
                self.callback(self.net_ready)

    def __init__(self, cb, verbose: bool = False):
        # Initialize state
        self.net_ready = False
        self.modem_ready = False

        # Initialize configuration
        self.verbose = verbose
        self.callback = cb

        # Start periodic callback
        self.periodic_timer = canvas.Timer(PERIODIC_TIMER, False, self.periodic_cb, None)

        # Initialize modem, if present
        try:
            from canvas_net import Modem
            self.has_modem = True
            self.modem = Modem(self.modem_cb)
        except:
            # No modem, so it's ready
            self.has_modem = False
            self.modem = None
            self.modem_ready = True

        # Initialize network
        self.nic = network.Zephyr()
        self.nic.ifconfig("dhcp")

    def wait_for_ready(self):
        # Wait for the modem to be ready
        wait_counter = 0
        if self.modem is not None:
            while self.modem_ready == False and wait_counter < MODEM_READY_LIMIT:
                time.sleep_ms(100)
                wait_counter += 1
            if wait_counter >= MODEM_READY_LIMIT:
                raise Exception("Timeout waiting for modem ready")

        # Wait for the network to be ready
        wait_counter = 0
        while self.nic.isconnected() == False and wait_counter < NETWORK_READY_LIMIT:
            time.sleep_ms(100)
            wait_counter += 1
        if wait_counter >= NETWORK_READY_LIMIT:
            raise Exception("Timeout waiting for network ready")

        # Ready to go
        self.net_ready = True

    def is_ready(self):
        return self.net_ready
