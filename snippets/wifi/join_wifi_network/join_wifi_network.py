# Connect as a "station" to an infrastructure Wi-Fi network
import network

# Join an internet-connected Wi-Fi network. For simplicity, the
# Wi-Fi credentials are hard-coded.
nic = network.WLAN(network.WLAN.IF_STA)   # Create the network interface
nic.active(True)                          # Enable the interface
# Join the network. For simplicity, retries are not implemented here.
nic.connect('MY_WIFI_SSID', 'MY_WIFI_PASSPHRASE') # Join the network
if(nic.isconnected()):
    print('Network joined, station IP:', nic.ifconfig()[0])
