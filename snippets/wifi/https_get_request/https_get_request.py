# This code demonstrates how to perform an HTTPS GET request providing
# the certificate chain to verify the server's certificate.
# It uses the `socket` and `ssl` modules to establish a secure connection.
import socket, sys
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
                print('done receiving content')
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
    print('Address:',addr)

    sock = socket.socket()

    try:
        if timeout is not None:
            assert SUPPORT_TIMEOUT, 'Socket does not support timeout'
            sock.settimeout(timeout)

        if proto == 'https:':
            assert SUPPORT_SSL, 'HTTPS not supported: could not find ssl'
            print('Wrapping in SSL')
            sock = ssl.wrap_socket(sock, **ssl_params)

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
        sys.print_exception(e)
        sock.close()
        raise e

    return resp


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)

# Certificate chain used to verify the server's certificate
ssl_params = {
    'cadata': '-----BEGIN CERTIFICATE-----\
MIIEXjCCA0agAwIBAgITB3MSSkvL1E7HtTvq8ZSELToPoTANBgkqhkiG9w0BAQsF\
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\
b24gUm9vdCBDQSAxMB4XDTIyMDgyMzIyMjUzMFoXDTMwMDgyMzIyMjUzMFowPDEL\
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEcMBoGA1UEAxMTQW1hem9uIFJT\
QSAyMDQ4IE0wMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALtDGMZa\
qHneKei1by6+pUPPLljTB143Si6VpEWPc6mSkFhZb/6qrkZyoHlQLbDYnI2D7hD0\
sdzEqfnuAjIsuXQLG3A8TvX6V3oFNBFVe8NlLJHvBseKY88saLwufxkZVwk74g4n\
WlNMXzla9Y5F3wwRHwMVH443xGz6UtGSZSqQ94eFx5X7Tlqt8whi8qCaKdZ5rNak\
+r9nUThOeClqFd4oXych//Rc7Y0eX1KNWHYSI1Nk31mYgiK3JvH063g+K9tHA63Z\
eTgKgndlh+WI+zv7i44HepRZjA1FYwYZ9Vv/9UkC5Yz8/yU65fgjaE+wVHM4e/Yy\
C2osrPWE7gJ+dXMCAwEAAaOCAVowggFWMBIGA1UdEwEB/wQIMAYBAf8CAQAwDgYD\
VR0PAQH/BAQDAgGGMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAdBgNV\
HQ4EFgQUwDFSzVpQw4J8dHHOy+mc+XrrguIwHwYDVR0jBBgwFoAUhBjMhTTsvAyU\
lC4IWZzHshBOCggwewYIKwYBBQUHAQEEbzBtMC8GCCsGAQUFBzABhiNodHRwOi8v\
b2NzcC5yb290Y2ExLmFtYXpvbnRydXN0LmNvbTA6BggrBgEFBQcwAoYuaHR0cDov\
L2NydC5yb290Y2ExLmFtYXpvbnRydXN0LmNvbS9yb290Y2ExLmNlcjA/BgNVHR8E\
ODA2MDSgMqAwhi5odHRwOi8vY3JsLnJvb3RjYTEuYW1hem9udHJ1c3QuY29tL3Jv\
b3RjYTEuY3JsMBMGA1UdIAQMMAowCAYGZ4EMAQIBMA0GCSqGSIb3DQEBCwUAA4IB\
AQAtTi6Fs0Azfi+iwm7jrz+CSxHH+uHl7Law3MQSXVtR8RV53PtR6r/6gNpqlzdo\
Zq4FKbADi1v9Bun8RY8D51uedRfjsbeodizeBB8nXmeyD33Ep7VATj4ozcd31YFV\
fgRhvTSxNrrTlNpWkUk0m3BMPv8sg381HhA6uEYokE5q9uws/3YkKqRiEz3TsaWm\
JqIRZhMbgAfp7O7FUwFIb7UIspogZSKxPIWJpxiPo3TcBambbVtQOcNRWz5qCQdD\
slI2yayq0n2TXoHyNCLEH8rpsJRVILFsg0jc7BaFrMnF462+ajSehgj12IidNeRN\
4zl+EoNaWdpnWndvSpAEkq2P\
-----END CERTIFICATE-----\
-----BEGIN CERTIFICATE-----\
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\
rqXRfboQnoZsG4q5WTP468SQvvG5\
-----END CERTIFICATE-----',\
    'server_hostname': 'www.ezurio.com'\
}

import network
nic = network.WLAN(network.WLAN.IF_STA)
nic.active(True)
nic.connect('MY_WIFI_SSID', 'MY_WIFI_PASSPHRASE')
if(nic.isconnected()):
    print('Network joined, station IP:', nic.ifconfig()[0])
    resp = get('https://www.ezurio.com', timeout=3, ssl_params=ssl_params)
    if resp is not None:
        print('Response status:', resp.status_code)
        print('Response message:', resp.message)
        print('Response headers:', resp.headers)
        content = resp.content()
        if content:
            print('Response content:', content[:100])  # Print first 100 bytes of content
    else:
        print('Failed to get a response')
    resp.close()
else:
    print('Failed to connect to the network, please verify SSID and passphrase')

