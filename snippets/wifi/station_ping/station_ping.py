# Join a Wi-Fi network and send a ping to a remote host
import network, time

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

    # Send a ping to a remote host. For simplicity, the remote host is hard-coded.
    hostname = 'micropython.org'              # remote host to ping
    for i in range(3):
        print('Pinging ' + hostname + '...')
        nic.ping(hostname)                        # send a ping
        time.sleep(1)

    nic.disconnect()                          # Disconnect from the network
except Exception as e:
    print('Error: ', e)
