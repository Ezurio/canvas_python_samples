# Connect to a TCP socket echo server.
import network, socket

# Join an internet-connected Wi-Fi network. For simplicity, the
# Wi-Fi credentials are hard-coded.
ssid = 'MY_WIFI_SSID'                         # Wi-Fi network name
passphrase = 'MY_WIFI_PASSPHRASE'             # Wi-Fi network password
print('Joining network ' + ssid + '...')
try:
    # Join the network. For simplicity, retries are not implemented here.
    nic = network.WLAN(network.WLAN.IF_STA)   # Create the network interface
    nic.active(True)                          # Enable the interface
    nic.connect(ssid, passphrase)             # Join the network
    print('Network joined, station IP:', nic.ifconfig()[0])

    # Create a socket and send a packet to an echo server
    hostname = 'tcpbin.com'                              # Echo server name
    port = 4242                                          # Echo server port
    print("Opening socket connection to: " + hostname + ":" + str(port))
    sock = socket.socket()                               # Create the socket
    addr = socket.getaddrinfo(hostname, port)[0][-1]     # Get server address
    sock.connect(addr)                                   # Connect the socket
    payload = 'Hello, Socket!\n'                         # Create a string to send
    print(' Writing:', payload.encode())
    bytes_written = sock.write(payload)                  # Send a string
    data = sock.read(bytes_written)                      # Receive a string
    print('Received:', data)
    sock.close()                                         # Close the socket
    print('Closed socket')
    nic.disconnect()                                     # Disconnect from the network
    print('Finished\n')
except Exception as e:
    print('Error: ', e)
