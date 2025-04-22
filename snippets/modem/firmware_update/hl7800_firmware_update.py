"""This sample demonstrates how to update the modem firmware with an update file
that exists on the file system.
WARNING:
This will take a while to complete (several minutes depending on the update file size).
DO NOT reset the Pinnacle 100 or remove power during the update process.
"""
import canvas_net


FS_BASE_PATH = '/lfs1/scripts/'
# Change this filename to the correct firmware file you want to use
UPDATE_FILE = '4.7.1.0.rc10_to_4.7.1.0.rc12.ua'


done = False


def modem_cb(e: tuple):
    """Callback function for modem events."""
    global modem, done
    print("Modem event: {}".format(e))
    if e.event == modem.EVENT_STATE and e.data[0] == modem.STATE_INITIALIZED:
        print("Modem initialized successfully")
        if not done:
            modem.update_firmware(FS_BASE_PATH + UPDATE_FILE)
    elif e.event == modem.EVENT_FOTA_STATE:
        if e.data[0] == modem.STATE_FOTA_START:
            print("Starting firmware update")
        elif e.data[0] == modem.STATE_FOTA_WIP:
            print("Firmware update in progress")
        elif e.data[0] == modem.STATE_FOTA_FILE_ERROR:
            print("Firmware update file error!")
        elif e.data[0] == modem.STATE_FOTA_INSTALL:
            print("Firmware update install")
        elif e.data[0] == modem.STATE_FOTA_REBOOT_AND_RECONFIGURE:
            print("Firmware update reboot and reconfigure modem")
        elif e.data[0] == modem.STATE_FOTA_COMPLETE:
            print("Firmware update complete!")
            done = True
        else:
            print("Firmware update state: {}".format(e.data[0]))


modem = canvas_net.Modem(modem_cb)
