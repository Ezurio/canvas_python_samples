# Get the MAC address from the Wi-Fi network interface
import network

nic = network.WLAN(network.STA_IF)  # Get the station interface (STA_IF)
mac_address = nic.config('mac').hex()  # Get the MAC address of the NIC
print('MAC:', mac_address)  # Print the MAC address in hexadecimal format

