import canvas_ble as ble
from canvas_ble import UUID
from state_machine import StateMachine
import machine, os

# Extend the canvas_ble.Scanner with custom scan filter methods
class CustomScanner(ble.Scanner):
    def __init__(self, scan_cb):
        super().__init__(scan_cb)
        self.filter_name = None
        self.filter_uuid = None
        self.filter_address = None
        self.filter_manuf_data = None
        self.filter_raw_data = None

    def set_filter_by_name(self, name):
        self.filter_name = name

    def set_filter_by_uuid(self, uuid):
        self.filter_uuid = uuid
    
    def set_filter_by_address(self, address):
        self.filter_address = address

    def set_filter_by_manuf_data(self, manuf_data):
        self.filter_manuf_data = manuf_data
    
    def set_filter_by_raw_data(self, raw_data):
        self.filter_raw_data = raw_data

    def start_scan(self):
        #
        #   Setup a scan filter, then start a scan.
        #   The following filter types are supported:
        #
        #   canvas_ble.Scanner.FILTER_NAME: The data parameter is a string. The name of the
        #   device in the advertisement must match the string in its entirety.
        #
        #   canvas_ble.Scanner.FILTER_UUID: The data parameter is a UUID string. The size of
        #   the data determines the UUID type to filter on. Two bytes of data are required for a
        #   16-bit UUID, four bytes of data are required for a 32-bit UUID, and 16 bytes of data
        #   are required for a 128-bit UUID.
        #
        #   canvas_ble.Scanner.FILTER_ADDR: The data parameter is a BLE address byte string, in the
        #   same format as provided by canvas_ble.my_addr() or as returned in a scan callback in the
        #   "addr" property of the event passed to the scan callback handler.
        #
        #   canvas_ble.Scanner.FILTER_MANUF_DATA: The data parameter is a byte string of manufacturer
        #   data. This data is compared to the manufacturer data in the advertisement. The first two
        #   bytes of the data are always the manufacturer ID. The filter data can be smaller than the
        #   advertisement data to allow matching only on the manufacturer ID or manufacturer ID and a
        #   portion of the manufacturer-specific data.
        #
        #   canvas_ble.Scanner.FILTER_DATA: The data parameter is a byte string of generic data. The
        #   filter matches if the data in the advertisement contains the filter data in its entirety
        #   at any location.
        #
        self.filter_reset()
        if self.filter_name is not None:
            self.filter_add(ble.Scanner.FILTER_NAME, self.filter_name)
        elif self.filter_uuid is not None:
            self.filter_add(ble.Scanner.FILTER_UUID, self.filter_uuid)
        elif self.filter_address is not None:
            self.filter_add(ble.Scanner.FILTER_ADDR, self.filter_address)
        elif self.filter_manuf_data is not None:
            self.filter_add(ble.Scanner.FILTER_MANUF_DATA, self.filter_manuf_data)
        elif self.filter_raw_data is not None:
            self.filter_add(ble.Scanner.FILTER_DATA, self.filter_raw_data)
        else:
            print("No filter set, not scanning")
            return
        # Start scanning (active)
        self.start(1)

    def stop_scan(self):
        # Stop scanning
        self.stop()

# Extend the StateMachine class with the state machine logic for this application
class BLEScannerWithConnect(StateMachine):
    # List of events that the state machine can handle
    _events = ['init_event', 'scan_result_found_event', 'connected_event', 'disconnect_event']
    # Initial state of the state machine
    _start = 'scanning_state'
    # List of states that the state machine can be in
    _states = ['scanning_state', 'connecting_state', 'connected_state']

    def __init__(self, scan_cb):
        super().__init__()
        # Create a custom scanner
        self.scanner = CustomScanner(scan_cb)

    # 'scanning' state: BLE is scanning and waiting for a connection
    def scanning_state(self, event):
        if event == 'init_event' or event == 'disconnect_event':
            print("Scanning...")
            # Start scanning
            try:
                self.scanner.start_scan()
            except Exception as e:
                print("Error: ", e, "\r\nRebooting...")
                machine.reset()
        
        if event == 'scan_result_found_event':
            print("Found device '" + ble.addr_to_str(app.peer_address) + "', connecting...")
            # Connect to the found device
            self.scanner.stop_scan()
            self._set('connecting_state')
            self.connecting_state(event)

    def connecting_state(self, event):
        if event == 'scan_result_found_event':
            # connect to the found device
            app.connection = ble.connect(app.peer_address, ble.PHY_1M,
                app.connected_cb, app.disconnected_cb)

        # Wait for a connection event
        if event == 'connected_event':
            print("Connected")
            self._set('connected_state')

    def connected_state(self, event):
        # TODO: Add application logic for the connected state here

        # Wait for a disconnection event
        if event == 'disconnect_event':
            print("Disconnected")
            self._set('scanning_state')
            # Trigger the disconnect event in the scanning state
            self.scanning_state(event)

# The main application class
class App:
    app_id = 'ble_scanner_with_connect'
    app_ver = '0.1.0'

    def __init__(self):
        # Display app info
        print("System:", os.uname().sysname, "\r\nBoard:",
            os.uname().machine, "\r\nBuild:", os.uname().release)
        print("App ID:", self.app_id, "\r\nApp Version:", self.app_ver)
        # Initialize BLE
        ble.init()
        print("My BLE Address:", ble.addr_to_str(ble.my_addr()))
        print("--------------------------------\r\n")
        # Set the "connected" and "disconnected" event callbacks
        ble.set_periph_callbacks(self.connected_cb, self.disconnected_cb)
        # Create the state machine
        self.state_machine = BLEScannerWithConnect(self.scan_cb)
        # Initialize connection variables
        self.peer_address = None
        self.connection = None
    
    # Set the filter type to use for the scanner
    def add_filter(self, filter_type, *args):
        if filter_type == "name":
            print("Setting filter by name: " + args[0])
            self.state_machine.scanner.set_filter_by_name(args[0])
        elif filter_type == "uuid":
            print("Setting filter by UUID: " + str(args[0]))
            self.state_machine.scanner.set_filter_by_uuid(args[0])
        elif filter_type == "address":
            print("Setting filter by address: " + ble.addr_to_str(args[0]))
            self.state_machine.scanner.set_filter_by_address(args[0])
        elif filter_type == "manuf_data":
            print("Setting filter by manufacturer data: ", args[0].hex())
            self.state_machine.scanner.set_filter_by_manuf_data(args[0])
        elif filter_type == "raw_data":
            print("Setting filter by raw data: ", args[0].hex())
            self.state_machine.scanner.set_filter_by_raw_data(args[0])
    
    # Start the state machine
    def start_state_machine(self):
        # Start the state machine
        self.state_machine.init_event()

    # BLE "scan" callback
    def scan_cb(self, event):
        # Connect to the found device
        self.peer_address = event.addr
        self.state_machine.scan_result_found_event()

    # BLE "connected" callback
    def connected_cb(self, conn):
        # Notify the state machine of the connection event
        self.state_machine.connected_event()

    # BLE "disconnected" callback
    def disconnected_cb(self, conn):
        # Notify the state machine of the disconnection event
        self.state_machine.disconnect_event()

# Start the application
app = App()

# Uncomment the following lines to add filters of different types
app.add_filter("name", "CanvasAd")
#app.add_filter("uuid", UUID("11223344-5566-7788-99aabbcc-ddeeff00"))
#app.add_filter("address", ble.str_to_addr("00B43A3104B279"))
#app.add_filter("manuf_data", bytes.fromhex("7700"))
#app.add_filter("raw_data", bytes.fromhex("7700"))

# Start the state machine
app.start_state_machine()
