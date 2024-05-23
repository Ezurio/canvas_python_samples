import sys
from at_string import ATString

class ATReader:
    def __init__(self, stream_in, stream_out):
        self.echo = True
        self.stream_in = stream_in
        self.stream_out = stream_out

    def write(self, data: str):
        self.stream_out.write(data)

    def read_cmd(self) -> ATString:
        while True:
            # Get a line of text from the input
            cmd_str = ""
            while True:
                c = self.stream_in.read(1)
                if type(c) is bytes:
                    c = c.decode("utf-8")
                    if c == '\r':
                        c = '\n'
                        if self.echo:
                            self.write('\r\n')
                    else:
                        if self.echo:
                            self.write(c)
                else:
                    if self.echo:
                        self.write(c)
                if c == '\n':
                    break
                cmd_str += c

            # Parse the AT command string
            try:
                at_cmd = ATString(cmd_str)
            except:
                self.write("ERROR\r\n")
                continue

            # Return the parsed command
            return at_cmd

    def set_echo(self, echo: bool):
        self.echo = echo
