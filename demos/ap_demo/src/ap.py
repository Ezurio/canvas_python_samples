import network

class Ap:
    def __init__(self):
        self.nic = network.WLAN(network.WLAN.IF_AP)
    
    def start(self, ssid, passphrase):
        self.nic.active(True)
        self.ssid = ssid
        self.passphrase = passphrase
        self.nic.config(essid=self.ssid, password=self.passphrase)

    def stop(self):
        self.nic.config(essid='', password='')
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
