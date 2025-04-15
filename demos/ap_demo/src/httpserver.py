import os
import sys
import socket

class HttpServer:
    mime_types = {
        'html': 'text/html',
        'htm': 'text/html',
        'shtml': 'text/html',
        'css': 'text/css',
        'json': 'application/json',
        'js': 'application/javascript',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'ico': 'image/icon',
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        'bin': 'application/octet-stream',
        'exe': 'application/octet-stream',
        'dll': 'application/octet-stream',
        'so': 'application/octet-stream',
        'a': 'application/octet-stream',
        'o': 'application/octet-stream',
        'obj': 'application/octet-stream',
        'lib': 'application/octet-stream',
        'mpy': 'application/octet-stream',
        'pyc': 'application/octet-stream',
        'zip': 'application/octet-stream'
    }

    def __init__(self, config):
        self.server_socket = None
        self.conn = None
        self.client_address = None
        self.config = config
        self.max_chunk_size = 1024
        self.wwwroot = ''
        self.post_handlers = {}
        self.get_handlers = {}

    def url_parse(url):
        l = len(url)
        data = bytearray()
        i = 0
        while i < l:
            if url[i] != '%':
                d = ord(url[i])
                i += 1
            
            else:
                d = int(url[i+1:i+3], 16)
                i += 3
            
            data.append(d)
        
        return data.decode('utf8').strip()
    
    def get_content_type(path):
        extension = path.split('.')[-1]
        content_type = 'text/plain'
        if extension in HttpServer.mime_types:
            content_type = HttpServer.mime_types[extension]
        return content_type

    def get_redirect(self):
        return '''HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                <head><meta http-equiv="refresh" content="0;url=/"><script type="text/javascript">window.location.href = "/index.html";</script></head>
                <body>Redirecting...</body>'''

    def send_chunked(self, conn, response):
        for i in range(0, len(response), self.max_chunk_size):
            chunk = response[i:i+self.max_chunk_size]
            if isinstance(chunk, str):
                conn.send(chunk.encode("utf-8"))
            elif isinstance(chunk, bytes):
                conn.send(chunk)
            else:
                conn.send(str(chunk).encode("utf-8"))

    def register_post_handler(self, path, handler):
        self.post_handlers[path] = handler

    def register_get_handler(self, path, handler):
        self.get_handlers[path] = handler
    
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
            try:
                os.stat(path)
                return True
            except OSError:
                pass
            try:
                path += '.gz'
                os.stat(path)
                return True
            except OSError:
                return False
        except OSError:
            return False

    def accepts_gzip(self, header_lines):
        for line in header_lines:
            if line.startswith('Accept-Encoding:'):
                if 'gzip' in line:
                    return True
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
                        #else:
                        #    print('\r\nReceived data: %s\r\n' % request)

                    # Close connection if network error
                    if network_error:
                        continue

                    headers, body = request.split('\r\n\r\n', 1)
                    content_length = 0
                    
                    # Find the content length if specified
                    for line in headers.split('\r\n'):
                        if line.startswith('Content-Length:'):
                            content_length = int(line.split(' ')[1])
                            break
                    
                    #print('Content length: %d\r\n' % content_length)

                    # If content length is specified, read the body
                    if content_length > 0:
                        while len(body) < content_length:
                            chunk = str(self.conn.recv(1024), "utf8")
                            if len(chunk) == 0:
                                network_error = True
                                break
                            body += chunk
                        if network_error:
                            continue
                    
                    # Parse the first line for request type
                    header_lines = headers.split('\r\n')
                    method = header_lines[0].split(' ')[0]
                    request_path = header_lines[0].split(' ')[1]

                    #print('Method: %s, Request path: %s\r\n' % (method, request_path))
                    
                    if network_error:
                        print('Network error, closing connection')
                        continue

                    if len(request_path) == 0:
                        print('Invalid request path')
                        continue
                    
                    if method == 'POST':
                        # Handle POST request
                        if request_path in self.post_handlers:
                            handler = self.post_handlers[request_path]
                            if handler(self, self.conn, header_lines, body) == False:
                                continue
                            else:
                                break
                        else:
                            #self.send_chunked(self.conn, 'HTTP/1.1 404 Not Found\r\n\r\n')
                            self.send_chunked(self.conn, self.get_redirect())
                    elif method == 'GET':
                        #print('GET request: %s\r\n' % request_path)
                        # Handle GET request
                        if request_path in self.get_handlers:
                            handler = self.get_handlers[request_path]
                            if handler(self, self.conn, header_lines, body) == False:
                                continue
                            else:
                                break
                        elif self.resource_exists(request_path, True):
                            request_path = self.clean_path(request_path)
                            header = ''
                            #print('resource exists: %s\r\n' % request_path)
                            cache_header = 'max-age=3600' # Use 'no-cache,no-store' here for dynamic content
                            if self.accepts_gzip(header_lines) and self.resource_exists(request_path+'.gz', False):
                                file_size = os.stat(request_path+'.gz').st_size
                                content_type = HttpServer.get_content_type(request_path)
                                header = 'HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Encoding: gzip\r\nContent-Length: %d\r\nCache-Control: %s\r\n\r\n' % (content_type, file_size, cache_header)
                                request_path += '.gz'
                            else:
                                # Determine the length of the file
                                file_size = os.stat(request_path).st_size
                                content_type = HttpServer.get_content_type(request_path)
                                header = 'HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\nCache-Control: %s\r\n\r\n' % (content_type, file_size, cache_header)
                            if header != '':
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
                            #self.send_chunked(self.conn, 'HTTP/1.1 404 Not Found\r\n\r\n')
                            # Redirect to index.html on 'Not Found'
                            self.send_chunked(self.conn, self.get_redirect())
                except Exception as e:
                    #sys.print_exception(e)
                    pass
                finally:
                    self.conn.close()
        except Exception as e:
            #sys.print_exception(e)
            pass
        except KeyboardInterrupt:
            pass
        finally:
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None

HttpServer.url_parse = staticmethod(HttpServer.url_parse)
HttpServer.get_content_type = staticmethod(HttpServer.get_content_type)
