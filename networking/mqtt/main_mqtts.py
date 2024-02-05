import time
from net_helper import NetHelper
from mqtt import MQTTClient

##############################################################################
# Configuration
#
# Fill out the following configuration parameters to match your environment.
# For simplicity, the certificates/keys are stored as strings in this example.
# In a real application, you would store them in a more secure location.

client_id = "my-device"
hostname = "mqtt.example.com"
port = 8883
client_cert = """-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
"""
client_key = """-----BEGIN EC PRIVATE KEY-----
...
-----END EC PRIVATE KEY-----
"""
ca_cert = """-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
"""
topic = "my-topic"
data = "Hello, MQTT!"

#
##############################################################################

# Wait for network to come up
print("Waiting for network")
net = NetHelper(None)
net.wait_for_ready()

# Connect the MQTT client
mqtt = MQTTClient(
    client_id,
    hostname,
    port=port,
    keepalive=60,
    ssl=True,
    ssl_params = {
        "cert": client_cert,
        "key": client_key,
        "cadata": ca_cert,
        "server_hostname": hostname
    })
mqtt.connect()

# Publish a message
print("Publishing message")
mqtt.publish(topic, data)

# Disconnect the MQTT client
mqtt.disconnect()
