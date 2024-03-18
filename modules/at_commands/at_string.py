class ATString:
    """
    Class to parse an AT command string. The string is parsed into the
    following fields:

      - command: The AT command (e.g. "I" for "ATI"). This is always an
          upper-case string, regardless of the case of the input string.
      - parameter: The parameter (e.g. "0" for "ATI0"). This is always a list
          of parameters to account for commands like "ATI0,1,2" where the
          parameter would be `[0, 1, 2]`.
      - operator: The operator (e.g. "=" for "ATI0="). This can be None if
          there is no operator.
      - value: The value (e.g. "1" for "ATI0=1"). The value is only present
          when the operator is =.

    :param string: The string to parse.
    """
    def __minus_quotes(string):
        out = ""
        quote = False
        for i in range(len(string)):
            if string[i] == '"':
                quote = not quote
            elif quote == False:
                out += string[i]
        return out

    def __split_minus_quotes(string, delim):
        out = []
        quote = False
        start = 0
        for i in range(len(string)):
            if string[i] == '"':
                quote = not quote
            elif quote == False and string[i] == delim:
                out.append(string[start:i].strip())
                start = i+1
        out.append(string[start:].strip())
        return out

    def __repr__(self):
        return "ATString(command={}, parameter={}, operator={}, value={})".format(
            self.command, self.parameter, self.operator, self.value)

    def __init__(self, string):
        self.command = None
        self.parameter = None
        self.operator = None
        self.value = None

        # Strip trailing whitespace
        string = string.rstrip()

        # If empty string, treat as empty command
        if len(string) == 0:
            return

        # Anything else must start with "AT"
        if string.upper().startswith("AT") == False:
            raise ValueError("Command must start with AT")
        string = string[2:]

        # Empty "AT" command
        if len(string) == 0:
            self.command = ''
            return

        # Extract the command
        self.command = ''
        for i in range(len(string)):
            if string[i].isdigit() or string[i].isspace():
                break
            elif string[i] == "=" or string[i] == "?":
                break
            else:
                self.command += string[i]
        string = string[len(self.command):]
        self.command = self.command.upper()

        # Done if we're out of characters
        if len(string) == 0:
            return

        # Check for an operator
        string_minus = ATString.__minus_quotes(string)
        if "=?" in string_minus:
            if string[-2:] != "=?":
                raise ValueError("=? must be at end of string")
            self.operator = "=?"
            string = string[:-2]

            # Extract the parameter (if any)
            if len(string) > 0:
                self.parameter = [ int(string) ]
            return
        elif "?" in string_minus:
            if string[-1:] != "?":
                raise ValueError("? must be at end of string")
            self.operator = "?"
            string = string[:-1]

            # Extract the parameter (if any)
            if len(string) > 0:
                self.parameter = [ int(string) ]
            return
        elif "=" in string_minus:
            self.operator = "="
            minus_idx = string.index("=")
            self.parameter = [ int(string[:minus_idx]) ]
            self.value = ATString.__split_minus_quotes(
                string[minus_idx+1:].strip(), ',')
            if len(self.value) == 1:
                self.value = self.value[0]
            else:
                raise ValueError("Invalid value")
            return

        # Done if we're out of characters
        if len(string) == 0:
            return

        # Extract parameters
        self.parameter = ATString.__split_minus_quotes(string.strip(), ',')
