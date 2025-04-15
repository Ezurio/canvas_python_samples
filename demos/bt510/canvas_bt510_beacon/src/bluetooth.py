import canvas_ble

class Bluetooth:
    ble_name = 'BT510'
    advertiser = None
    ble_enabled = False
    is_advertising = False
    device_id = None
    is_connectable = False
    is_scannable = False
    is_extended = True
    advertising_interval_ms = 1000
    ble_custom_data = b"\xb00\xb00"

    def __init__(self):
        pass

    def set_name(self, new_name):
        self.ble_name = new_name
        if self.ble_enabled and self.is_advertising:
            self.update_advertisement()

    def set_custom_data(self, new_data):
        self.ble_custom_data = new_data
        if self.ble_enabled and self.is_advertising:
            self.update_advertisement()
    
    def get_device_id(self):
        return self.device_id
    
    def set_tx_power(self, dbm):
        if self.ble_enabled:
            canvas_ble.set_tx_power(dbm*10)

    def ble_connected(self, conn):
        pass

    def ble_disconnected(self, conn):
        if self.is_advertising: 
            self.advertiser.start()

    def enable(self):
        if self.ble_enabled:
            return
        canvas_ble.init()
        canvas_ble.set_periph_callbacks(self.ble_connected, self.ble_disconnected)
        self.device_id = canvas_ble.addr_to_str(canvas_ble.my_addr())[10:12] + canvas_ble.addr_to_str(canvas_ble.my_addr())[12:14]
        self.advertiser = canvas_ble.Advertiser()
        self.ble_enabled = True

    def start_advertising(self, connectable=False, scannable=False, extended=True, advertising_interval_ms=1000):
        if self.ble_enabled and not self.is_advertising:
            self.is_connectable = connectable
            self.is_scannable = scannable
            self.is_extended = extended
            self.advertiser.set_properties(self.is_connectable, self.is_scannable, self.is_extended)
            self.advertising_interval_ms = advertising_interval_ms
            self.advertiser.set_interval(advertising_interval_ms, advertising_interval_ms + 10)
            self.update_advertisement()
            self.advertiser.start()
            self.is_advertising = True

    # Stop advertising
    def stop_advertising(self):
        if self.ble_enabled and self.is_advertising:
            self.advertiser.stop()
            self.is_advertising = False

    # Stop advertising
    def disable(self):
        if self.ble_enabled:
            if self.is_advertising:
                self.stop_advertising()
            # intentionally not setting ble_enabled = False here to avoid multiple calls to canvas_ble.init()

    # Update BLE Advertisement
    def update_advertisement(self):
        if self.ble_enabled:
            self.advertiser.clear_buffer(False)
            self.advertiser.add_ltv(0x01, bytes([0x06]), False)
            self.advertiser.add_tag_string(0x09, self.ble_name + '-' + self.device_id, False)
            self.advertiser.add_ltv(0xff, self.ble_custom_data, False)
            self.advertiser.update()
