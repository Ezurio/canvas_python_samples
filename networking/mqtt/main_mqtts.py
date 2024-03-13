from net_helper import NetHelper
from mqtt import MQTTClient
import binascii
import machine
import canvas

##############################################################################
# Configuration
#
# Fill out the following configuration parameters to match your environment.
# For simplicity, the certificates/keys are stored as strings in this example.
# In a real application, you would store them in a more secure location.

client_id = "my-device_" + binascii.hexlify(machine.unique_id()).decode()
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

# publish topic
topic_pub = "device/" + client_id + "/data"
data_pub = '{"messge":"hello!"}'

# subscribe topic
topic_sub = "device/" + client_id + "/control"

MQTT_KEEP_ALIVE_SECONDS = 300
MSG_WAIT_TIMEOUT_MS = 30000

#
##############################################################################

print("Running MQTTS example")
net = NetHelper(None)
print("Waiting for network...")
net.wait_for_ready()

# Connect the MQTT client
mqtt = MQTTClient(
    client_id,
    hostname,
    port=port,
    keepalive=MQTT_KEEP_ALIVE_SECONDS,
    ssl=True,
    ssl_params={
        "cert": client_cert,
        "key": client_key,
        "cadata": ca_cert,
        "server_hostname": hostname
    })


def subscribe_cb(topic, msg):
    print("MQTT subscribe msg", msg)


def mqtt_ping_timer_cb(event):
    print("MQTT ping")
    mqtt.ping()


mqtt.set_callback(subscribe_cb)

print("Connecting to MQTT as endpoint: {}".format(client_id))
mqtt.connect()

print("Subscribing to topic: {}".format(topic_sub))
mqtt.subscribe(topic_sub)

print("Publishing message to topic: {} with data: {}".format(topic_pub, data_pub))
mqtt.publish(topic_pub, data_pub)

mqtt_ping_timer = canvas.Timer(
    MQTT_KEEP_ALIVE_SECONDS * 1000, True, mqtt_ping_timer_cb, None)
mqtt_ping_timer.start()

while True:
    print("Waiting for MQTT message...")
    try:
        mqtt.wait_msg(MSG_WAIT_TIMEOUT_MS)
    except Exception as e:
        print(e)
