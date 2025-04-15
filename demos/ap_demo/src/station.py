import network

class Station:
    def __init__(self):
        self.nic = network.WLAN(network.WLAN.IF_STA)
    
    def connect(self, ssid, passphrase):
        self.nic.active(True)
        self.nic.connect(ssid, passphrase)

    def disconnect(self):
        self.nic.disconnect()
        self.nic.active(False)

    def is_connected(self):
        return self.nic.isconnected()
    
    def get_ip(self):
        return self.nic.ifconfig()[0]
    
    def get_mac(self):
        return self.nic.config('mac')
    
    def get_ssid(self):
        return self.nic.config('essid')
    
    def get_channel(self):
        return self.nic.config('channel')
    
    def get_rssi(self):
        return self.nic.status('rssi')
    
    def scan(self):
        return self.nic.scan()
