import os
import socket
try:
    import ssl
    SUPPORT_SSL = True
except ImportError:
    ssl = None
    SUPPORT_SSL = False

SUPPORT_TIMEOUT = hasattr(socket.socket, 'settimeout')


class Response():
    def __init__(self, status_code, raw, headers=None, msg=""):
        self.status_code = status_code
        self.raw = raw
        self._content = None
        self.headers = headers
        self.message = msg

    def content(self):
        if self._content is None:
            try:
                l = self.raw.read(1)
                self._content = l
                while len(l) > 0:
                    l = self.raw.read(1)
                    self._content += l
                self.raw.close()
                self.raw = None
            except:
                pass
        return self._content

    def close(self):
        if self.raw is not None:
            self._content = None
            self.raw.close()
            self.raw = None

    def raise_for_status(self):
        if 400 <= self.status_code < 500:
            raise OSError('Client error: %s' % self.status_code)
        if 500 <= self.status_code < 600:
            raise OSError('Server error: %s' % self.status_code)


# Adapted from upip
def request(method, url, content=None, content_type=None, timeout=None, headers=None, ssl_params=None):
    urlparts = url.split('/', 3)
    proto = urlparts[0]
    host = urlparts[2]
    urlpath = '' if len(urlparts) < 4 else urlparts[3]
    resp = None

    if proto == 'http:':
        port = 80
    elif proto == 'https:':
        port = 443
    else:
        raise OSError('Unsupported protocol: %s' % proto[:-1])

    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]

    sock = socket.socket()

    try:
        if timeout is not None:
            assert SUPPORT_TIMEOUT, 'Socket does not support timeout'
            sock.settimeout(timeout)

        # For Zephyr boards, connect before wrap
        if os.uname()[0] == 'zephyr':
            # print('Connecting to', addr)
            sock.connect(addr)

        if proto == 'https:':
            assert SUPPORT_SSL, 'HTTPS not supported: could not find ssl'
            # print('Wrapping in SSL')
            sock = ssl.wrap_socket(sock, **ssl_params)

        # For non-Zephyr boards, wrap before connect
        if os.uname()[0] != 'zephyr':
            # print('Connecting to', addr)
            sock.connect(addr)

        # print('Connected, sending request')
        sock.write('%s /%s HTTP/1.1\r\nHost: %s\r\n' % (method, urlpath, host))

        if headers is not None:
            for header in headers.items():
                sock.write('%s: %s\r\n' % header)

        if content is not None:
            sock.write('content-length: %s\r\n' % len(content))
            sock.write('content-type: %s\r\n' % content_type)
            sock.write('\r\n')
            sock.write(content)
        else:
            sock.write('\r\n')

        # print('reading response')
        l = sock.readline()
        protover, status, msg = l.split(None, 2)

        # Read headers
        line = sock.readline()
        headers = line
        while line != b'\r\n':
            line = sock.readline()
            headers += line

        resp = Response(int(status), sock, headers, msg)
    except Exception as e:
        sock.close()
        raise e

    return resp


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)
