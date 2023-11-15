import config
import device_db
import uwb_ble_connect
import uwb_ble_scanner
import uwb_ble_advertiser
import uwb_smp_client
import pi_ble_common
import sync
import led_strip
import PikaStdLib

def main():
    mem = PikaStdLib.MemChecker()
    mem.now()

    # Clean up after boot.py
    boot_led_strip = None
    led_strip = led_strip.led_strip("", 1)
    led_strip.set(0, 0)

    # Initialize the semaphore
    sync.init()

    # Initialize the BLE stack
    err = pi_ble_common.init()
    uwb_ble_scanner.init()
    uwb_ble_advertiser.init()
    uwb_ble_connect.init()

    # Load the configuration and device database
    config.load()
    device_db.load()
    mem.now()

    # Loop forever waiting for something to happen
    while True:
        # Update advertising state
        if config.is_ble_advertiser() == True:
            led_strip.set(0, 0x00000f)
            uwb_ble_advertiser.update()
        else:
            uwb_ble_advertiser.stop()

        # Update scanning state
        if uwb_ble_connect.is_pending() == False:
            if config.is_ble_scanner() == True:
                led_strip.set(0, 0x000f00)
                uwb_ble_scanner.start()
            else:
                uwb_ble_scanner.stop()

        # Wait for something to happen
        mem.now()
        sync.wait(-1)
        print("main wakeup")
        mem.now()

        # Process any BLE events
        uwb_ble_connect.connect_one()

        # Process any SMP events
        uwb_smp_client.service_one()

main()
