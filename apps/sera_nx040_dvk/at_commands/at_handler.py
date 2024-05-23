from at_string import ATString
import os
import sys
import gc
import binascii
import machine
import canvas_ble
import canvas_uwb

class ATHandler:
    ##########################################################################
    # Class interfaces
    ##########################################################################
    def __init__(self, reader):
        canvas_ble.init()
        self.uwb_sessions = { }
        self.reader = reader
        self.COMMANDS = {
            '': { 'params': (0, 0), 'handler': None },
            'E': { 'params': (1, 1), 'handler': self.__handle_ate },
            'I': { 'params': (1, 1), 'handler': self.__handle_ati },
            'Z': { 'params': (0, 0), 'handler' : self.__handle_atz },
            '+UWBS': { 'params': (2, 5), 'handler': self.__handle_uwbs },
            '+UWBSD': { 'params': (1, 1), 'handler': self.__handle_uwbsd },
            '+UWBSA': { 'params': (3, 3), 'handler': self.__handle_uwbsa },
            '+UWBSAM': { 'params': (2, 2), 'handler': self.__handle_uwbsam },
            '+UWBSAMX': { 'params': (2, 2), 'handler': self.__handle_uwbsamx },
            '+UWBSI': { 'params': (2, 2), 'handler': self.__handle_uwbsi },
            '+UWBSC': { 'params': (3, 3), 'handler': self.__handle_uwbsc },
            '+UWBSS': { 'params': (1, 1), 'handler': self.__handle_uwbss },
        }

    def handle_command(self, cmd: ATString):
        # Check for valid command
        if cmd.command not in self.COMMANDS:
            raise ValueError("Invalid command")

        # Check for valid parameter count
        param_len = len(cmd.parameter) if cmd.parameter is not None else 0
        if param_len < self.COMMANDS[cmd.command]['params'][0] or param_len > self.COMMANDS[cmd.command]['params'][1]:
            raise ValueError("Invalid parameter count")

        # Call the command handler
        if self.COMMANDS[cmd.command]['handler'] is not None:
            self.COMMANDS[cmd.command]['handler'](cmd)

    ##########################################################################
    # Private methods
    ##########################################################################
    def __uwb_range_cb_factory(self, session_id):
        def __uwb_range_cb(ranges):
            for r in ranges:
                self.reader.write("RANGE:" + str(session_id) + " " +
                                 str(r.addr) + " " + str(r.range) + "\r\n")
        return __uwb_range_cb

    ##########################################################################
    # Command handlers
    ##########################################################################
    def __handle_ate(self, cmd: ATString):
        self.reader.set_echo(int(cmd.parameter[0]) == 1)

    def __handle_ati(self, cmd: ATString):
        # Get the parameter
        i = int(cmd.parameter[0])

        if i == 0:
            self.reader.write(os.uname().machine)
        elif i == 3:
            self.reader.write(os.uname().release)
        elif i == 5:
            self.reader.write(binascii.hexlify(machine.unique_id()).decode())
        elif i == 4:
            self.reader.write(canvas_ble.addr_to_str(canvas_ble.my_addr()))
        elif i == 2001:
            self.reader.write(str(machine.reset_cause()))
        elif i == 2002:
            self.reader.write(str(gc.mem_free()))
        elif i == 2003:
            self.reader.write(str(gc.mem_alloc()))
        else:
            raise ValueError("Invalid device info ID")
        self.reader.write("\r\n")

    def __handle_atz(self, cmd: ATString):
        machine.reset()

    def __handle_uwbs(self, cmd: ATString):
        global uwb_sessions

        # Get the mandatory parameters
        session_id = int(cmd.parameter[0])
        role = int(cmd.parameter[1])

        # Convert the role into the proper value
        if role == 0:
            role = canvas_uwb.ROLE_INITIATOR
        elif role == 1:
            role = canvas_uwb.ROLE_RESPONDER
        else:
            raise ValueError("Invalid role")

        # Make sure that we don't already have a session with this ID
        if session_id in self.uwb_sessions:
            raise ValueError("Session already exists")

        # Create a new session, but only in RAM, not with the actual radio yet
        self.uwb_sessions[session_id] = {}
        self.uwb_sessions[session_id]["session"] = None
        self.uwb_sessions[session_id]["role"] = role
        self.uwb_sessions[session_id]["type"] = 0
        self.uwb_sessions[session_id]["preamble"] = 9
        self.uwb_sessions[session_id]["channel"] = 9
        self.uwb_sessions[session_id]["local_addr"] = None
        self.uwb_sessions[session_id]["peer_addr"] = [ ]
        self.uwb_sessions[session_id]["interval"] = 500
        self.uwb_sessions[session_id]["app_config"] = { }

        # Set the optional parameters
        if len(cmd.parameter) == 3:
            session_type = int(cmd.parameter[2])
            if session_type != 0 and session_type != 1:
                raise ValueError("Invalid session type")
            self.uwb_sessions[session_id]["type"] = session_type
        if len(cmd.parameter) == 4:
            self.uwb_sessions[session_id]["preamble"] = int(cmd.parameter[3])
        if len(cmd.parameter) == 5:
            self.uwb_sessions[session_id]["channel"] = int(cmd.parameter[4])

    def __handle_uwbsd(self, cmd: ATString):
        # Get the session ID
        session_id = int(cmd.parameter[0])

        # Do nothing if the session doesn't exist
        if session_id not in self.uwb_sessions:
            return

        # If the session is active, stop it
        if self.uwb_sessions[session_id]["session"] is not None:
            self.uwb_sessions[session_id]["session"].stop()
            self.uwb_sessions[session_id]["session"].close()
            self.uwb_sessions[session_id]["session"] = None

        # Delete the session
        del self.uwb_sessions[session_id]

    def __handle_uwbsa(self, cmd: ATString):
        # Get the session ID
        session_id = int(cmd.parameter[0])

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")
            
        # Session cannot be active
        if self.uwb_sessions[session_id]["session"] is not None:
            raise ValueError("Session is already active")

        # Set the local and peer addresses
        self.uwb_sessions[session_id]["local_addr"] = int(cmd.parameter[1])
        self.uwb_sessions[session_id]["peer_addr"] = [ int(cmd.parameter[2]) ]

    def __handle_uwbsam(self, cmd: ATString):
        # Get the session ID and new address
        session_id = int(cmd.parameter[0])
        address = int(cmd.parameter[1])

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")

        # Only supported on multicast sessions
        if self.uwb_sessions[session_id]["type"] == 0:
            raise ValueError("Session is not multicast")

        # Check to see if the address is already in the list
        if address in self.uwb_sessions[session_id]["peer_addr"]:
            # Already there, do nothing
            return

        # Add the peer address
        self.uwb_sessions[session_id]["peer_addr"].append(address)

        # If the session is active, add the peer address
        if self.uwb_sessions[session_id]["session"] is not None:
            self.uwb_sessions[session_id]["session"].add_multicast(address)

    def __handle_uwbsamx(self, cmd: ATString):
        # Get the session ID and address to delete
        session_id = int(cmd.parameter[0])
        address = int(cmd.parameter[1])

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")

        # Only supported on multicast sessions
        if self.uwb_sessions[session_id]["type"] == 0:
            raise ValueError("Session is not multicast")

        # Check to see if the address is already in the list
        if address not in self.uwb_sessions[session_id]["peer_addr"]:
            # Not there, do nothing
            return

        # Delete the peer address
        self.uwb_sessions[session_id]["peer_addr"].remove(address)

        # If the session is active, delete the peer address
        if self.uwb_sessions[session_id]["session"] is not None:
            self.uwb_sessions[session_id]["session"].del_multicast(address)

    def __handle_uwbsi(self, cmd: ATString):
        # Get the session ID and interval
        session_id = int(cmd.parameter[0])
        interval = int(cmd.parameter[1])

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")
            
        # Set the ranging interval
        self.uwb_sessions[session_id]["interval"] = interval

        # If the session is active, update the interval
        if self.uwb_sessions[session_id]["session"] is not None:
            self.uwb_sessions[session_id]["session"].set_ranging_interval(interval)

    def __handle_uwbsc(self, cmd: ATString):
        # Get the session ID, configuration ID, and configuration value
        session_id = int(cmd.parameter[0])
        config_id = int(cmd.parameter[1])
        config_value = binascii.unhexlify(cmd.parameter[2].strip('"').encode())

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")

        # Set the configuration
        self.uwb_sessions[session_id]["app_config"][config_id] = config_value

        # If the session is active, update the configuration
        if self.uwb_sessions[session_id]["session"] is not None:
            self.uwb_sessions[session_id]["session"].set_app_config(
                config_id, config_value)

    def __handle_uwbss(self, cmd: ATString):
        # Get the session ID
        session_id = int(cmd.parameter[0])

        # Make sure that we have a session with this ID
        if session_id not in self.uwb_sessions:
            raise ValueError("Session does not exist")

        # Make sure that the session is not already active
        if self.uwb_sessions[session_id]["session"] is not None:
            raise ValueError("Session is already active")

        # Check to see if we have other active sessions
        active_sessions = False
        for k, v in self.uwb_sessions.items():
            if v["session"] is not None:
                active_sessions = True
                break

        # If no other active sessions, initialize the UWB stack
        if not active_sessions:
            canvas_uwb.init()
            canvas_uwb.raw_uci_send(bytes([0x2e, 0x2f, 0x00, 0x01, 0x01]))

        # Create a new session
        session = canvas_uwb.session_new(session_id, self.uwb_sessions[session_id]["role"])
        self.uwb_sessions[session_id]["session"] = session

        # Set the parameters
        session.set_ranging_interval(self.uwb_sessions[session_id]["interval"])
        session.set_local_addr(self.uwb_sessions[session_id]["local_addr"])
        session.set_peer_addr(self.uwb_sessions[session_id]["peer_addr"][0])
        session.set_app_config(canvas_uwb.CONFIG_MULTI_NODE_MODE,
            bytes([self.uwb_sessions[session_id]["type"]]))
        session.set_app_config(canvas_uwb.CONFIG_PREAMBLE_CODE_INDEX,
            bytes([self.uwb_sessions[session_id]["preamble"]]))
        session.set_channel(self.uwb_sessions[session_id]["channel"])
        session.set_callback(self.__uwb_range_cb_factory(session_id))
        for k, v in self.uwb_sessions[session_id]["app_config"].items():
            session.set_app_config(k, v)

        # Start the session
        session.start()

        # Add the multicast addresses, must be done after starting the session
        for addr in self.uwb_sessions[session_id]["peer_addr"][1:]:
            session.add_multicast(addr)
