import time
from net_helper import NetHelper
from mqtt import MQTTClient

##############################################################################
# Configuration
#
# Fill out the following configuration parameters to match your environment.

client_id = "my-device"
hostname = "mqtt.example.com"
port = 1883
username = "my-username"
password = "my-password"
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
    user=username,
    password=password,
    keepalive=60)
mqtt.connect()

# Publish a message
print("Publishing message")
mqtt.publish(topic, data)

# Disconnect the MQTT client
mqtt.disconnect()
