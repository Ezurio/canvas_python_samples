from canvas import Timer
import canvas_ble as ble
import binascii
import time

#
# XbitTextService
#
# This class implements a BLE service that allows a connected client to send
# and receive text messages. It is primarily intended for use when connecting
# to Xbit Desktop/Mobile applets.
#
class XbitTextService:
    #--------------------------------------
    # Variables
    #--------------------------------------
    ble_name = "Xbit Text"
    service_uuid = "22ac5df9-f794-46b1-a7ee-f1198f9430bc"
    message_characteristic_uuid = "22ac0002-f794-46b1-a7ee-f1198f9430bc"
    response_characteristic_uuid = "22ac0003-f794-46b1-a7ee-f1198f9430bc"
    message_to_send = ""
    new_message_to_send = False
    my_gattserver = None
    update_timer = None
    connection = None
    do_notify = False
    discon = False
    advert = None
    cb_app_connected = None
    cb_app_message_received = None
    gatt_table = None

    def __init__(self, cb_app_connected, cb_app_message_received):
        self.cb_app_connected = cb_app_connected
        self.cb_app_message_received = cb_app_message_received

        # GATT table definition
        self.gatt_table = {
            "Service 1":{
                "Name": "Xbit Text Service",
                "UUID": self.service_uuid,
                "Characteristic 1":{
                    "Name": "message",
                    "UUID" : self.message_characteristic_uuid,
                    "Length" : 140,
                    "Read Encryption" : "None",
                    "Write Encryption" : "None",
                    "Capability" : "Notify",
                    "Callback" : self.cb_notify_enabled
                },
                "Characteristic 2":{
                    "Name": "response",
                    "UUID" : self.response_characteristic_uuid,
                    "Length" : 140,
                    "Read Encryption" : "None",
                    "Write Encryption" : "None",
                    "Capability" : "Write",
                    "Callback" : self.cb_response_received
                }
            }
        }


    #--------------------------------------
    # Callbacks
    #--------------------------------------
    def cb_notify_enabled(self, event_object):
        if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
            self.do_notify = False

        if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
            if self.cb_app_connected != None:
                self.cb_app_connected()
            self.do_notify = True

    def cb_response_received(self, event_object):
        if self.cb_app_message_received != None:
            self.cb_app_message_received(event_object.data.decode())
        pass

    def cb_con(self, conn):
        self.connection = conn
        print("Connected")
        self.discon = False

    def cb_discon(self, conn):        
        print("Disconnected")
        self.discon = True
        self.advert.start()
        
        # Delete the connection once it's disconnected.
        if self.connection != None:
            del(self.connection)
            self.connection = None
            self.printMyName()

    def cb_timer(self, event):
        if self.new_message_to_send:
            # Update the advertisement data
            self.update_advert()

            if self.connection != None and self.do_notify:
                # Create a message
                value = bytes(self.message_to_send,'utf-8')
                # Notify the connected client
                try:
                    self.my_gattserver.notify(self.connection, "message", value)
                except:
                    print("Notify error")
            
            self.new_message_to_send = False

    def uuidToBytes(self, uuid): # Convert the 128 bit UUID string to bytes
        uuid_bytes = list(bytes.fromhex(uuid.replace("-", "")))
        uuid_bytes.reverse()
        return bytes(uuid_bytes)

    #--------------------------------------
    # Methods
    #--------------------------------------
    # Update the advertisement data
    def update_advert(self):
        # Setup flag byte array
        flags = [6]
        flag_bytes=bytes(flags)
        self.advert.clear_buffer(False)
        self.advert.add_ltv(1, flag_bytes, False)
        uuid_bytes = self.uuidToBytes(self.service_uuid)
        self.advert.add_ltv(7, uuid_bytes, False)
        mfg_data_hdr = b"\x77\x00\xc0\x00"
        self.advert.add_tag_string(9, self.ble_name, False)
        self.advert.add_ltv(0xff, mfg_data_hdr + self.message_to_send.encode(), False)
        self.advert.update()

    # Start advertising the XbitTextService
    def start(self):
        print('Starting Xbit Text Service...')
        # Start an advert
        ble.init()
        self.message_to_send = "Hello from " + self.ble_name + " (" + binascii.hexlify(bytes(list(ble.my_addr())[::-1][:6])).decode().upper() + ")"
        self.advert = ble.Advertiser()
        self.advert.stop()
        self.advert.set_phys(ble.PHY_1M, ble.PHY_2M)
        self.advert.set_properties(True, False, True)
        self.advert.set_interval(240, 250)
        self.advert.start()
        self.update_advert()

        # Define the gatt server and callbacks
        ble.set_periph_callbacks(self.cb_con, self.cb_discon)
        self.my_gattserver = ble.GattServer()
        self.my_gattserver.build_from_dict(self.gatt_table)

        # Start the GATT server
        self.my_gattserver.start()

        # Set the timer callback
        self.update_timer = Timer(100, True, self.cb_timer, {})
        self.update_timer.start()

    # Print this device's BLE name and Bluetooth device address
    def printMyName(self):
        print("My BLE Name is: \033[38;5;15m" + self.ble_name + " (" + binascii.hexlify(bytes(list(ble.my_addr())[::-1][:6])).decode().upper() + ")\033[0m")
        print("Awaiting Connection...")

    def setName(self, name):
        self.ble_name = name
        self.message_to_send = "Hello from " + self.ble_name + " (" + binascii.hexlify(bytes(list(ble.my_addr())[::-1][:6])).decode().upper() + ")"
        self.update_advert()

    # Send a message to the connected device
    def send(self, message):
        self.message_to_send = message
        self.new_message_to_send = True
        # Give time for the timer callback to send a notification for the message
        time.sleep_ms(100)
