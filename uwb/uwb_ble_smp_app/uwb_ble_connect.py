import device_db
import config
import pi_ble_common
import pi_ble_connection
import uwb_ble_advertiser
import uwb_ble_scanner
import sync
import PikaStdLib

# List of connections we would like to make
waiting_connections = []

# List of connections we are trying to make
pending_connections = []

# List of active connections that are not matched in the database
unclaimed_connections = []

# Active connections that are matched in the database
active_connections = []

class Connection:
    def __init__(self, ble_addr: bytes, db: device_db.Device):
        self.ble_addr = ble_addr
        self.db = db
        self.conn = None
        self.incoming = False

    def __del__(self):
        if self.db is not None:
            self.db.disconnected()

    def is_incoming(self) -> bool:
        print("conn is incoming", self.incoming)
        return self.incoming

    def disconnect(self):
        if self.conn is not None:
            self.conn.disconnect()

# Add a device to the list of devices we would like to connect to
def add(ble_addr: bytes, db: device_db.Device):
    global waiting_connections

    # Only add new connections
    for c in waiting_connections:
        if c.ble_addr == ble_addr:
            # Already in the list
            return

    waiting_connections.append(Connection(ble_addr, db))

    # Wake up the main loop
    sync.signal()

# Connect to the next waiting connection
def connect_one():
    global waiting_connections
    global pending_connections

    if len(waiting_connections) == 0:
        # No waiting connections
        return

    # Get the next connection to attempt
    c = waiting_connections.pop(0)

    # Stop scanning
    uwb_ble_scanner.stop()

    # Make the connection
    print("Current", PikaStdLib.MemChecker.getNow())
    print("Attempting BLE connection to", pi_ble_common.addr_to_str(c.ble_addr))
    c.conn = pi_ble_connection.connect(c.ble_addr, pi_ble_common.PHY_1M,
        central_connect, central_disconnect)

    # If this was successful, add to pending list
    pending_connections.append(c)

    # If there are more waiting connections, run this again
    if len(waiting_connections) > 0:
        # Wake up the main loop again
        sync.signal()

def central_connect(conn):
    global pending_connections
    global active_connections

    print("Current", PikaStdLib.MemChecker.getNow())
    print("Connected as central to", pi_ble_common.addr_to_str(conn.get_addr()))

    # Find the connection in the pending list
    found = False
    for c in pending_connections:
        if c.conn == conn:
            # No longer pending
            print("Current a", PikaStdLib.MemChecker.getNow(), c)
            found = True
            pending_connections.remove(c)

            # Add to the active list
            print("Current b", PikaStdLib.MemChecker.getNow(), c)
            active_connections.append(c)

            # We are connected
            print("Current c", PikaStdLib.MemChecker.getNow(), c)
            c.db.connected(c)

    # If we didn't find the connection, close it
    if found == False:
        conn.disconnect()

    # Restart scanning after connection
    #uwb_ble_scanner.start()

def central_disconnect(conn):
    global pending_connections
    global active_connections

    print("Disconnected as central from", pi_ble_common.addr_to_str(conn.get_addr()))

    # Search the pending list first
    for c in pending_connections:
        if c.conn == conn:
            # No longer pending
            pending_connections.remove(c)

    # Search the active list
    for c in active_connections:
        if c.conn == conn:
            # No longer active
            active_connections.remove(c)

            # We are disconnected
            c.db.disconnected()

    # Restart scanning after connection
    uwb_ble_scanner.start()

def periph_connect(conn):
    global unclaimed_connections

    print("Connected as peripheral to", pi_ble_common.addr_to_str(conn.get_addr()))

    # Add this to the unclaimed connections list
    c = Connection(conn.get_addr(), None)
    c.conn = conn
    c.incoming = True
    unclaimed_connections.append(c)

    # Restart advertising after a connection
    uwb_ble_advertiser.update()

def periph_disconnect(conn):
    global unclaimed_connections
    global active_connections

    print("Disconnected as peripheral from", pi_ble_common.addr_to_str(conn.get_addr()))

    # Search the unclaimed list
    for c in unclaimed_connections:
        if c.conn == conn:
            # No longer unclaimed
            unclaimed_connections.remove(c)

    # Search the active list
    for c in active_connections:
        if c.conn == conn:
            # No longer active
            active_connections.remove(c)

            # We are disconnected
            c.db.disconnected()

def claim_connection(ble_addr: bytes, db: device_db.Device):
    global unclaimed_connections
    global active_connections

    # Search the unclaimed list
    for c in unclaimed_connections:
        if c.ble_addr == ble_addr:
            # No longer unclaimed
            unclaimed_connections.remove(c)

            # Add to the active list
            active_connections.append(c)

            # We are connected
            c.db = db
            c.db.connected(c)

# Initializer to ensure we can receive connections as a peripheral
def init():
    err = pi_ble_connection.set_periph_callbacks(periph_connect, periph_disconnect)

def is_pending():
    return len(pending_connections) > 0