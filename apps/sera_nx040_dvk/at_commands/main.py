import machine
import sys
from at_handler import ATHandler
from at_reader import ATReader

def __main__():
    # Create the command reader
    reader = ATReader()

    # Create the command handler
    handler = ATHandler(reader)

    # Command handling loop
    sys.stdout.write("\r\nOK\r\n")
    while True:
        cmd = reader.read_cmd()
        if cmd is None:
            continue
        if cmd.command is None:
            continue

        try:
            handler.handle_command(cmd)
            sys.stdout.write("OK\r\n")
        except Exception as e:
            sys.stdout.write("ERROR\r\n")

# Check the state of the user button
p = machine.Pin("GPIO7", machine.Pin.IN, machine.Pin.PULL_UP)
if p.value() == 0:
    # Button is pressed, don't run main loop
    print("Button pressed, not running main loop")
    del p
else:
    # Button is not pressed, run main loop
    del p
    __main__()
