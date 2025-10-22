"""
This sample demonstrates how to update the firmware of a Canvas device from a file in the filesystem.
The firmware is updated from a file in the root directory of the file system.

Requirements:
- A firmware file must be present in the root directory of the file system. If not specified, the default file name 'update.bin' will be used.
- After this script runs, invoke the 'update_firmware()' function from the REPL to start the firmware update process.
- The update_firmware('my_firmware.bin') function can be called with an optional argument specifying the file name of the firmware update file.
"""

import canvas
import machine
import os
import time

READ_SIZE = 2048
REBOOT_DELAY_SECS = 5
updating = False


def update_firmware(file_name='update.bin'):
    global dfu, updating
    file_size = 0

    if updating:
        print('Already updating firmware')
        return

    try:
        file_size = os.stat(file_name)[6]
    except:
        print('File {} does not exist'.format(file_name))
        return

    try:
        f = open(file_name, 'rb')
    except:
        print('File {} could not be opened'.format(file_name))
        return

    updating = True

    written = 0
    final = False
    while written < file_size:
        data = f.read(READ_SIZE)
        if len(data) == 0:
            break
        if (file_size - written) <= READ_SIZE:
            final = True
        dfu.write(data, final)
        written = dfu.bytes_written()
        print('\r\tUpdating {}% ({}/{})..........'.format(round(written /
              file_size * 100.0), written, file_size), end='')

    print('\r\nImage written')
    dfu.request_upgrade()
    print('Upgrade requested, rebooting in {} seconds...'.format(REBOOT_DELAY_SECS))
    time.sleep(REBOOT_DELAY_SECS)
    updating = False
    machine.reset()


print('Firmware version: ', os.uname().release)

dfu = canvas.DFU()

print('image swap type: ', dfu.get_image_swap_type())

if not dfu.is_image_confirmed():
    print('image is NOT confirmed, confirming...')
    dfu.confirm_image()
    print('confirmed')
else:
    print('image is confirmed')
