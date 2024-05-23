import machine
import sys
import os
from at_handler import ATHandler
from at_reader import ATReader

def __main__():
    if os.uname().machine == 'sera_nx040_click':
        print("Starting AT command handler on UART0")
        # On the click board, open a UART
        uart = machine.UART(0)
        uart.init(115200)
        stream_in = uart
        stream_out = uart
    else:
        # On other boards, just reuse the REPL
        stream_in = sys.stdin
        stream_out = sys.stdout
    
    # Create the command reader
    reader = ATReader(stream_in, stream_out)

    # Create the command handler
    handler = ATHandler(reader)

    # Command handling loop
    stream_out.write("\r\nOK\r\n")
    while True:
        cmd = reader.read_cmd()
        if cmd is None:
            continue
        if cmd.command is None:
            continue

        try:
            handler.handle_command(cmd)
            stream_out.write("OK\r\n")
        except Exception as e:
            stream_out.write("ERROR\r\n")

# Check the state of the user button
if os.uname().machine == 'sera_nx040_click':
    p = machine.Pin("BUTTON", machine.Pin.IN, machine.Pin.PULL_UP)
else:
    p = machine.Pin("GPIO7", machine.Pin.IN, machine.Pin.PULL_UP)
if p.value() == 0:
    # Button is pressed, don't run main loop
    print("Button pressed, not running main loop")
    del p
else:
    # Button is not pressed, run main loop
    del p
    __main__()
