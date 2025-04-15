import socket

class WebHook:
    def __init__(self, url: str):
        self.url = url
        self.server = url.split("/")[2]
        self.path = url.split("/")[3]
        self.port = 80
        self.addr = socket.getaddrinfo(self.server, self.port)[0][-1]
    
    def send_message(self, message: str):
        # Placeholder for sending message to the webhook URL
        #print("Sending message to %s: %s" % (self.url, message))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.sock.write(('POST /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s' % (self.path, self.server, len(message), message)).encode())
        self.sock.close()
        self.sock = None
