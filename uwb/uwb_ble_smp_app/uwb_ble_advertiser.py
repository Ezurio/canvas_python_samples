import ble_ad_flags
import config
import pi_ble_advertising

# Global for the advertiser object
advertiser = None

# Global manufacturing data array
manu_data_hdr = [ ]

# Function to update the advertising data
def update():
    global advertiser
    global manu_data_hdr

    # Stop advertising
    err = advertiser.stop()
    err = advertiser.clear_buffer(0)

    # Set flags
    manu_flags = 0
    if config.is_configured():
        manu_flags = manu_flags | ble_ad_flags.CONFIGURED
    if config.is_ble_scanner():
        manu_flags = manu_flags | ble_ad_flags.BLE_SCANNER
    if config.is_uwb_responder():
        manu_flags = manu_flags | ble_ad_flags.UWB_ROLE_RESPONDER

    # Poke data into array
    manu_data_hdr[4] = config.network_id() & 0xff
    manu_data_hdr[5] = config.network_id() >> 8
    manu_data_hdr[6] = manu_flags & 0xff
    manu_data_hdr[7] = manu_flags >> 8

    # Add TLVs to advertisement
    err = advertiser.add_ltv(0x01, bytes([0x06]), 0)
    err = advertiser.add_ltv(0xff, bytes(manu_data_hdr), 0)
    err = advertiser.start()
    print("BLE advertiser updated", err)

def stop():
    err = advertiser.stop()
    print("BLE advertiser stopped", err)

def init():
    global advertiser
    global manu_data_hdr

    # Build the fixed portion of the advertisement
    manu_data_hdr = [0x77, 0x00]
    manu_data_hdr += [0x0C, 0x00, 0x00, 0x00, 0x00, 0x00]
    manu_data_hdr += list(config.device_id_bytes())
    manu_data_hdr += [0x00, 0x00, 0x00, 0x00]

    advertiser = pi_ble_advertising.advertising()
    err = advertiser.set_properties(1, 0, 1)
    err = advertiser.set_interval(200, 300)
    print("BLE advertiser initialized")
