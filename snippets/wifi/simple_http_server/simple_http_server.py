# Joins a WiFi network and starts a very basic HTTP server.
import os, sys, network, socket

# Simple HTTP server class that serves .html files from the
# local filesystem directory. Note the `index.html` file
# included with this snippet must also be copied to the device.
class SimpleHttpServer:
    def __init__(self):
        self.server_socket = None
        self.conn = None
        self.client_address = None
        self.max_chunk_size = 1024
        self.wwwroot = ''

    def send_chunked(self, conn, response):
        for i in range(0, len(response), self.max_chunk_size):
            chunk = response[i:i+self.max_chunk_size]
            if isinstance(chunk, str):
                conn.send(chunk.encode("utf-8"))
            elif isinstance(chunk, bytes):
                conn.send(chunk)
            else:
                conn.send(str(chunk).encode("utf-8"))
    
    def clean_path(self, path):
        if path.endswith('/'):
            path = path + 'index.html'
        else:
            path = self.wwwroot + path
        return path

    def resource_exists(self, path, clean):
        if clean:
            path = self.clean_path(path)
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def start_sync(self, bind_ip, bind_port):
        if self.server_socket:
            return
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('HTTP server started on %s:%d' % (bind_ip, bind_port))
        self.server_socket.bind((bind_ip, bind_port))
        self.server_socket.listen(1)
        # Handle HTTP requests
        try:
            while True:
                request = ''
                network_error = False
                try:
                    # This blocks until a client connects
                    self.conn, self.client_address = self.server_socket.accept()

                    # Receive the headers until "\r\n\r\n"
                    while request.find('\r\n\r\n') == -1:
                        request += str(self.conn.recv(1024), "utf8")
                        if len(request) == 0:
                            print('No data received, closing connection')
                            network_error = True
                            break

                    # Close connection if network error
                    if network_error:
                        continue

                    headers, body = request.split('\r\n\r\n', 1)
                    
                    # Parse the first line for request type
                    header_lines = headers.split('\r\n')
                    method = header_lines[0].split(' ')[0]
                    request_path = header_lines[0].split(' ')[1]

                    if network_error:
                        print('Network error, closing connection')
                        continue

                    if len(request_path) == 0:
                        print('Invalid request path')
                        continue

                    if method == 'GET':
                        if self.resource_exists(request_path, True):
                            request_path = self.clean_path(request_path)
                            cache_header = 'max-age=3600' # Use 'no-cache,no-store' here for dynamic content
                            # Determine the length of the file
                            file_size = os.stat(request_path).st_size
                            content_type = 'text/html' # only handle serving html for this simple server
                            header = 'HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\nCache-Control: %s\r\n\r\n' % (content_type, file_size, cache_header)
                            try:
                                self.send_chunked(self.conn, header)
                                f = open(request_path, 'rb')
                                response = f.read(128)
                                while response != b'':
                                    self.send_chunked(self.conn, response)
                                    response = f.read(128)
                                f.close()
                            except Exception as e:
                                sys.print_exception(e)
                                pass
                        else:
                            self.send_chunked(self.conn, 'HTTP/1.1 404 Not Found\r\n\r\n')
                except Exception as e:
                    pass
                finally:
                    self.conn.close()
        except Exception as e:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None

# Join a Wi-Fi network. For simplicity, the credentials are hard-coded.
nic = network.WLAN(network.WLAN.IF_STA)   # Create the network interface
nic.active(True)                          # Enable the interface
# Join the network. For simplicity, retries are not implemented here.
nic.connect('MY_WIFI_SSID', 'MY_WIFI_PASSPHRASE') # Join the network
if(nic.isconnected()):
    print('Network joined, station IP:', nic.ifconfig()[0])
    # Start the HTTP server
    server = SimpleHttpServer()
    server.start_sync(nic.ifconfig()[0], 80)
else:
    print('Failed to join network')
    sys.exit(1)
