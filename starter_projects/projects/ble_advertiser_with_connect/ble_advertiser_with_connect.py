import canvas_ble as ble
from canvas_ble import UUID
from state_machine import StateMachine
import machine, os, time

# Extend the canvas_ble.Advertiser with custom ad data
class CustomAdvertiser(ble.Advertiser):
    def __init__(self):
        super().__init__()
        self.advertised_name = "CanvasAd"
        self.custom_gatt_service_uuid = UUID("11223344-5566-7788-99aabbcc-ddeeff00")
    
    def start_advertisement(self):
        # Custom advertisement data
        #self.stop()
        self.clear_buffer(True)
        self.clear_buffer(False)
        self.add_ltv(ble.AD_TYPE_FLAGS, bytes([6]), False)
        self.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, self.advertised_name, False)
        self.add_ltv(ble.AD_TYPE_UUID128_COMPLETE, bytes(self.custom_gatt_service_uuid), False)
        self.manuf_data = bytes([0x77, 0x00, 0xFE, 0xED, 0xBE, 0xE5])
        self.add_ltv(ble.AD_TYPE_MANU_SPECIFIC, self.manuf_data, False)
        self.set_properties(True, False, True)
        self.set_interval(200, 250)
        self.start()

# Extend the StateMachine class with the state machine logic for this application
class BLEAdvertiserWithConnect(StateMachine):
    # List of events that the state machine can handle
    _events = ['init_event', 'connected_event', 'disconnect_event']
    # Initial state of the state machine
    _start = 'advertising_state'
    # List of states that the state machine can be in
    _states = ['advertising_state', 'connected_state']

    def __init__(self):
        super().__init__()
        # Create a custom advertiser
        self.advertiser = CustomAdvertiser()

    # 'advertising' state: BLE is advertising and waiting for a connection
    def advertising_state(self, event):
        global start_advertising
        if event == 'init_event' or event == 'disconnect_event':
            print("Advertising...")
            # Start advertising
            try:
                self.advertiser.start_advertisement()
            except Exception as e:
                print("Error: ", e, "\r\nRebooting...")
                machine.reset()
        
        # Wait for a connection event
        if event == 'connected_event':
            print("Connected")
            self._set('connected_state')
    
    def connected_state(self, event):
        # Wait for a disconnection event
        if event == 'disconnect_event':
            print("Disconnected")
            self._set('advertising_state')
            # Trigger the disconnect event in the advertising state
            self.advertising_state(event)

# The main application class
class App:
    app_id = 'ble_advertiser_with_connect'
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
        self.state_machine = BLEAdvertiserWithConnect()
        # Start the state machine
        self.state_machine.init_event()

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
