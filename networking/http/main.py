"""
This script demonstrates how to perform HTTP GET and POST requests using the `http_client` module.
From the REPL, http_get() and http_post() functions can be called to issue GET and POST requests, respectively.
"""

from net_helper import NetHelper
import http_client

hostname = "https://postman-echo.com"
ca_cert = """-----BEGIN CERTIFICATE-----
MIIFnjCCBUOgAwIBAgIQD8I/8RPYyQ+m7UuVBWHxrzAKBggqhkjOPQQDAjBKMQsw
CQYDVQQGEwJVUzEZMBcGA1UEChMQQ2xvdWRmbGFyZSwgSW5jLjEgMB4GA1UEAxMX
Q2xvdWRmbGFyZSBJbmMgRUNDIENBLTMwHhcNMjMwODE0MDAwMDAwWhcNMjQwODEy
MjM1OTU5WjBrMQswCQYDVQQGEwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTEWMBQG
A1UEBxMNU2FuIEZyYW5jaXNjbzEZMBcGA1UEChMQQ2xvdWRmbGFyZSwgSW5jLjEU
MBIGA1UEAxMLcG9zdG1hbi5jb20wWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASd
PqhBLXd422rzAUNSdpwu0zZcuLkV5qNjAIFM8am0vz+jYxsqBs2QSJf9hQEwJgnK
jgT6UKikmFC9QThJpzC7o4ID6DCCA+QwHwYDVR0jBBgwFoAUpc436uuwdQ6UZ4i0
RfrZJBCHlh8wHQYDVR0OBBYEFFmWPx8cWE5CKhN9hAaIbw5bxJs5MIGtBgNVHREE
gaUwgaKCC3Bvc3RtYW4uY29tghEqLmNkbi5wb3N0bWFuLmNvbYIRKi5zcnYucG9z
dG1hbi5jb22CECouZ28ucG9zdG1hbi5jb22CECouaWQucG9zdG1hbi5jb22CESou
bWFjLnBvc3RtYW4uY29tghAqLmd3LnBvc3RtYW4uY29tgg0qLnBvc3RtYW4uY29t
ghUqLmV4cGxvcmUucG9zdG1hbi5jb20wDgYDVR0PAQH/BAQDAgeAMB0GA1UdJQQW
MBQGCCsGAQUFBwMBBggrBgEFBQcDAjB7BgNVHR8EdDByMDegNaAzhjFodHRwOi8v
Y3JsMy5kaWdpY2VydC5jb20vQ2xvdWRmbGFyZUluY0VDQ0NBLTMuY3JsMDegNaAz
hjFodHRwOi8vY3JsNC5kaWdpY2VydC5jb20vQ2xvdWRmbGFyZUluY0VDQ0NBLTMu
Y3JsMD4GA1UdIAQ3MDUwMwYGZ4EMAQICMCkwJwYIKwYBBQUHAgEWG2h0dHA6Ly93
d3cuZGlnaWNlcnQuY29tL0NQUzB2BggrBgEFBQcBAQRqMGgwJAYIKwYBBQUHMAGG
GGh0dHA6Ly9vY3NwLmRpZ2ljZXJ0LmNvbTBABggrBgEFBQcwAoY0aHR0cDovL2Nh
Y2VydHMuZGlnaWNlcnQuY29tL0Nsb3VkZmxhcmVJbmNFQ0NDQS0zLmNydDAMBgNV
HRMBAf8EAjAAMIIBfgYKKwYBBAHWeQIEAgSCAW4EggFqAWgAdgDuzdBk1dsazsVc
t520zROiModGfLzs3sNRSFlGcR+1mwAAAYn0QqxnAAAEAwBHMEUCIEZy4KfCaY1I
c7sXhQq090BEYREreeA1Xb6H+qrBqiq5AiEAs0eDegl8ErfyC+hGw2mu0LlORk13
4vDp7AH4zzKcZvsAdwBIsONr2qZHNA/lagL6nTDrHFIBy1bdLIHZu7+rOdiEcwAA
AYn0QqxaAAAEAwBIMEYCIQDl1rJNqPzZv73wi0NOi78XXburl5XiO8knjSvgkGr/
xgIhAN/aGeRAVreG/Zn5MNr1om0Rqe4C0bYpwWMBPcMJb4yvAHUA2ra/az+1tiKf
m8K7XGvocJFxbLtRhIU0vaQ9MEjX+6sAAAGJ9EKsJQAABAMARjBEAiA98k9bq+TC
hO/GkY+mw4GlRxnUJE1l+R3Ut+m3yr69rwIgRVfgSq5qLvVF5tJ9/axDMgDrqaVP
4PCunjDrT1Fqn40wCgYIKoZIzj0EAwIDSQAwRgIhANzyabGnjODovueDdb0qGQMU
vs1zCbwTBqZYQGVPcTFCAiEA8tMs4XVXhVr2ktN4LliOqWOFvbn2nULgFiOEdC9g
+nA=
-----END CERTIFICATE-----
"""

resp = None


def http_get():
    """
    Sends an HTTP GET request to a specified endpoint.

    This function issues an HTTP GET request to the specified endpoint, with the following parameters:
    - `timeout`: The maximum time to wait for socket read/write operations.
    - `ssl_params`: SSL parameters for the request.

    After sending the request, it prints the status code of the response, reads and prints the content of the response,
    and then closes the response.

    Note: The global variable `resp` is used to store the response object.
    """
    global resp
    resp = None
    print("Issue HTTP GET...")
    resp = http_client.get(hostname + '/get?msg=hello',
                           timeout=6,
                           ssl_params={
                               "cadata": ca_cert,
                               "server_hostname": hostname})
    print("GET status: %d" % resp.status_code)
    print("Reading content...")
    content = resp.content()
    if content:
        print("Content:\n%s" % content.decode('utf-8'))
    else:
        print("No content")
    resp.close()


def http_post():
    """
    Sends an HTTP POST request to a specified endpoint.

    This function issues an HTTP POST request to the specified endpoint, with the following parameters:
    - `content_type`: The content type of the request payload.
    - `content`: The request payload.
    - `timeout`: The maximum time to wait for socket read/write operations.
    - `ssl_params`: SSL parameters for the request.

    After sending the request, it prints the status code of the response, reads and prints the content of the response,
    and then closes the response.

    Note: The global variable `resp` is used to store the response object.

    """
    global resp
    resp = None
    print("Issue HTTP POST...")
    resp = http_client.post(hostname + '/post',
                            content_type="application/json",
                            content='{"msg": "hello"}',
                            timeout=6,
                            ssl_params={
                                "cadata": ca_cert,
                                "server_hostname": hostname})
    print("POST status: %d" % resp.status_code)
    print("Reading content...")
    content = resp.content()
    if content:
        print("Content:\n%s" % content.decode('utf-8'))
    else:
        print("No content")
    resp.close()


net = NetHelper(None)
print("Connecting to network...")
net.wait_for_ready()
print("Connected to network")
