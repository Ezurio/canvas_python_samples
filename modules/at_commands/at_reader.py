import sys
from at_string import ATString

class ATReader:
    def __init__(self):
        self.echo = True

    def read_cmd(self) -> ATString:
        while True:
            # Get a line of text from the input
            cmd_str = ""
            while True:
                c = sys.stdin.read(1)
                if self.echo:
                    sys.stdout.write(c)
                if c == '\n':
                    break
                cmd_str += c

            # Parse the AT command string
            try:
                at_cmd = ATString(cmd_str)
            except:
                sys.stdout.write("ERROR\r\n")
                continue

            # Return the parsed command
            return at_cmd

    def set_echo(self, echo: bool):
        self.echo = echo
