# Join a Wi-Fi network and post a JSON payload to a webhook URL.
import network, socket, json

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
    if(nic.isconnected()):
        print('Network joined, station IP:', nic.ifconfig()[0])

        # Create a socket and send a JSON payload to a webhook URL
        hostname = 'webhook.site'                            # Webhook server name
        port = 80                                            # Webhook server port
        print("Opening socket connection to: " + hostname + ":" + str(port))
        sock = socket.socket()                               # Create the socket
        addr = socket.getaddrinfo(hostname, port)[0][-1]     # Get server address
        sock.connect(addr)                                   # Connect the socket
        # Create a JSON string to send
        payload = json.dumps({"key0": "value0", "key1": "value1"})
        webhook_url = '/275e5229-bcc4-45a0-b8ad-f2beb2676485'# Webhook URL
        # Create the HTTP request
        http_request = 'POST ' + webhook_url + ' HTTP/1.1\r\n' + \
            'Host: ' + hostname + '\r\n' + \
            'Content-Type: application/json\r\n' + \
            'Content-Length: ' + str(len(payload)) + '\r\n\r\n' + \
            payload
        # Send the HTTP request
        print('Sending HTTP request...')
        bytes_written = sock.write(http_request.encode())    # Send the HTTP request
        data = ''
        # Receive the response, may need to read in chunks
        print('Receiving response...')
        while True:
            try:
                chunk = sock.read(1)
            except Exception as e:
                break
            if len(chunk) > 0:
                data += chunk.decode()
        
        print('Received:\r\n' + data)
        sock.close()                                         # Close the socket
        # Close the socket and disconnect from the network
        print('Closed socket')
        nic.disconnect()                                     # Disconnect from the network
        print('Finished\n')
except Exception as e:
    print('Error: ', e)

