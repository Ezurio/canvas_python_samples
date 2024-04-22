import sntp
import config
import mqtt
import binascii
import machine
import canvas_net
import canvas_ble
import canvas
from net_helper import NetHelper
import os
import time
app_id = 'xbit_mg100_ble_to_mqtt'
app_ver = '1.1.0'

# Description: BLE to MQTT bridge
#
# All configuration for the application is stored in a CBOR file named
# config.cb. The file is read at startup and the configuration is stored in
# the Config class. The file is written only on a call to config.save().
#
# Configuration options for MQTT:
#   mqtt_topic: MQTT topic to publish to
#   mqtt_hostname: MQTT broker hostname
#   mqtt_port: MQTT broker port
#   mqtt_client_id: MQTT client ID
#   mqtt_user: MQTT username
#   mqtt_password: MQTT password
#   mqtt_client_cert_file: MQTT client certificate file
#   mqtt_client_key_file: MQTT client key file
#   mqtt_ca_cert_file: MQTT CA certificate file
#   mqtt_keepalive: MQTT keepalive period
#
# Configuration options for LwM2M (optional):
#   lwm2m_url: LwM2M server URL (or bootstrap server URL if lwm2m_bootstrap is set)
#   lwm2m_security_mode: LwM2M security mode (0 = PSK, 3 = no security)
#   lwm2m_bootstrap: 1 if using a bootstrap server, 0 otherwise
#   lwm2m_psk_id: LwM2M PSK ID (if lwm2m_security_mode is 0)
#   lwm2m_psk: LwM2M PSK (if lwm2m_security_mode is 0)
#   lwm2m_reg_update_time: LwM2M registration update time (if lwm2m_bootstrap is 0)
#
# Configuration options for SNTP (optional):
#    sntp_hostname: SNTP server hostname (optional, will use pool.ntp.org if not set)
#    sntp_period: SNTP update period (seconds, optional, will use 3600 if not set)
#
# If mqtt_user is set, then mqtt_password must also be set. If mqtt_user is
# not set, then mqtt_client_cert_file, mqtt_client_key_file, and
# mqtt_ca_cert_file must be set. mqtt_keepalive is optional and defaults to
# 60 seconds.
#
# The configuration values are set using config.set(key, value). Once all
# configuration values are set, config.save() must be called to write the
# configuration to the CBOR file.
#
# When the script is run for the first time and the configuration file does
# not exist, the configuration will be empty. The script will print a message
# indicating that the configuration is invalid and will raise an exception,
# which will cause the script to stop running and return to a REPL prompt.
# The user must then set the configuration values and call config.save() to
# write the configuration to the CBOR file. The board can be reset to run
# the script again.
#
# For example, to set the MQTT configuration:
#     >>> config.set("mqtt_topic", "mytopic")
#     >>> config.set("mqtt_hostname", "mybroker.com")
#     >>> config.set("mqtt_port", 8883)
#     >>> config.set("mqtt_client_id", "myclient")
#     >>> config.set("mqtt_user", "myuser")
#     >>> config.set("mqtt_password", "mypassword")
#     >>> config.save()
#
# The application will enable BLE scanning. When a BLE advertisement
# matching the filter is found, the temperature value is extracted from
# the manufacturer-specific data and published to the MQTT broker. If the
# temperature value changes by more than DELTA_TEMP degrees Celsius, the
# temperature is published. Otherwise, the temperature is published every
# PUBLISH_PERIOD milliseconds.
#
# The application will connect to the specific LwM2M server and register
# with it. If lwm2m_bootstrap is set, then the application will register
# with the bootstrap server and then register with the LwM2M server. If
# lwm2m_bootstrap is not set, then the application will register directly
# with the LwM2M server.


# Always send if delta is greater than this
DELTA_TEMP = 1.0

# Send every this many milliseconds
PUBLISH_PERIOD = 60000

# Print every this many milliseconds
PRINT_PERIOD = 10000

# LwM2M retry period
LWM2M_RETRY_PERIOD = 10000  # 10 seconds

# BLE scanner
scanner = None

# MQTT client
client = None

# Devices dictionary
#   key: device address (bytes)
#   value dictionary:
#      'temp': temperature (float, degrees Celsius)
#      'last_publish': last time published (int, milliseconds)
devices = {}


def scan_cb(evt):
    publish = False

    # Get manufacturer-specific data from the advertisement
    m = canvas_ble.find_ltv(0xff, evt.data)
    if m is None:
        return

    # Check if we've seen this device before
    if evt.addr not in devices:
        devices[evt.addr] = {'temp': 0.0, 'last_publish': 0}

    # Get the temperature from the manufacturer-specific data
    temp_bytes = m[len(m)-2:]
    temp_val = float(int.from_bytes(temp_bytes, "big"))
    temp = (((temp_val * 175720)/65536) - 46850) / 1000

    # Check if we should publish
    if abs(temp - devices[evt.addr]['temp']) >= DELTA_TEMP:
        publish = True
    elif time.ticks_ms() - devices[evt.addr]['last_publish'] >= PUBLISH_PERIOD:
        publish = True

    # Print if necessary
    if publish or (time.ticks_ms() - devices[evt.addr]['last_print']) >= PRINT_PERIOD:
        print("Device: {}, Temperature: {}".format(
            binascii.hexlify(evt.addr).decode(), temp))
        devices[evt.addr]['last_print'] = time.ticks_ms()

    # Publish if necessary
    if publish:
        # Publish the temperature
        print("Publishing")
        client.publish('{{"temperature": {}}}'.format(temp))
        devices[evt.addr]['last_publish'] = time.ticks_ms()
        devices[evt.addr]['temp'] = temp


class MqttClient:
    def __init__(self, config):
        self.client = None

        self.topic_str = config.get("mqtt_topic")
        if self.topic_str is None:
            raise Exception("mqtt_topic not set in configuration")

        self.hostname = config.get("mqtt_hostname")
        if self.hostname is None:
            raise Exception("mqtt_hostname not set in configuration")

        self.port = config.get("mqtt_port")
        if self.port is None:
            raise Exception("mqtt_port not set in configuration")

        self.client_id = config.get("mqtt_client_id")
        if self.client_id is None:
            raise Exception("mqtt_client_id not set in configuration")

        self.user = config.get("mqtt_user")
        if self.user is not None:
            self.password = config.get("mqtt_password")
            if self.password is None:
                raise Exception("mqtt_password not set in configuration")

        self.client_cert_file = config.get("mqtt_client_cert_file")
        if self.client_cert_file is not None:
            self.client_key_file = config.get("mqtt_client_key_file")
            if self.client_key_file is None:
                raise Exception(
                    "mqtt_client_key_file not set in configuration")

            self.ca_cert_file = config.get("mqtt_ca_cert_file")
            if self.ca_cert_file is None:
                raise Exception("mqtt_ca_cert_file not set in configuration")

        if self.client_cert_file is None and self.user is None:
            raise Exception(
                "Either mqtt_client_cert_file or mqtt_user must be set in configuration")

        self.keepalive = config.get("mqtt_keepalive")
        if self.keepalive is None:
            self.keepalive = 60

    def start(self):
        if self.user is not None:
            self.client = mqtt.MQTTClient(
                self.client_id,
                self.hostname,
                port=self.port,
                user=self.user,
                password=self.password,
                keepalive=self.keepalive)
        else:
            try:
                f = open(self.client_cert_file, "rb")
                client_cert = f.read()
                f.close()
            except:
                print("Error reading client certificate file")
                raise

            try:
                f = open(self.client_key_file, "rb")
                client_key = f.read()
                f.close()
            except:
                print("Error reading client key file")
                raise

            try:
                f = open(self.ca_cert_file, "rb")
                ca_cert = f.read()
                f.close()
            except:
                print("Error reading CA certificate file")
                raise

            self.client = mqtt.MQTTClient(
                self.client_id,
                self.hostname,
                port=self.port,
                keepalive=self.keepalive,
                ssl=True,
                ssl_params={
                    "cert": client_cert,
                    "key": client_key,
                    "cadata": ca_cert,
                    "server_hostname": self.hostname
                })

        # Connect the client
        try:
            self.client.connect()
        except:
            print("Connect failed")
            self.stop()

    def stop(self):
        if self.client is not None:
            try:
                self.client.disconnect()
            except:
                self.client.sock.close()
            self.client = None

    def publish(self, data):
        if self.client is None:
            try:
                self.start()
            except:
                print("Start failed")
                return

        try:
            self.client.publish(self.topic_str, data)
        except:
            print("Publish failed")
            self.stop()


class LwM2MClient:
    EVENTS = [
        "NONE",
        "BOOTSTRAP_REG_FAILURE",
        "BOOTSTRAP_REG_COMPLETE",
        "BOOTSTRAP_TRANSFER_COMPLETE",
        "REGISTRATION_FAILURE",
        "REGISTRATION_COMPLETE",
        "REG_TIMEOUT",
        "REG_UPDATE_COMPLETE",
        "DEREGISTER_FAILURE",
        "DISCONNECT",
        "QUEUE_MODE_RX_OFF",
        "ENGINE_SUSPENDED",
        "NETWORK_ERROR",
        "REG_UPDATE",
        "DEREGISTER"
    ]

    def __init__(self, config):
        self.client = None
        self.watchdog_timer = None
        self.restart_timer = None

        # Verify the configuration
        url = config.get("lwm2m_url")
        if url is None:
            print("lwm2m_url not set in configuration")
            return

        self.bootstrap = config.get("lwm2m_bootstrap")
        if self.bootstrap is None:
            self.bootstrap = 0
        if self.bootstrap != 0 and self.bootstrap != 1:
            raise Exception("Invalid lwm2m_bootstrap value in configuration")

        if self.bootstrap == 0:
            reg_update_time = config.get("lwm2m_reg_update_time")
            if reg_update_time is None:
                reg_update_time = 60

        security_mode = config.get("lwm2m_security_mode")
        if security_mode is None:
            security_mode = canvas_net.Lwm2m.SECURITY_NOSEC

        if security_mode == canvas_net.Lwm2m.SECURITY_PSK:
            psk_id = config.get("lwm2m_psk_id")
            psk = config.get("lwm2m_psk")
            if psk_id is None or psk is None:
                raise Exception(
                    "lwm2m_psk_id or lwm2m_psk not set in configuration")
        elif security_mode != canvas_net.Lwm2m.SECURITY_NOSEC:
            raise Exception("Invalid lwm2m_security_mode in configuration")

        # Set the endpoint name
        board_type = os.uname().machine
        if board_type == "bl5340_dvk_cpuapp":
            board_type = "bl5340"
        elif board_type == "pinnacle_100_dvk":
            board_type = "p100"
        endpoint = board_type + "_" + \
            binascii.hexlify(machine.unique_id()).decode()

        # Configure the LwM2M client
        self.client = canvas_net.Lwm2m(self.event_cb)
        self.client.set_endpoint_name(endpoint)
        self.client.set((self.client.OBJ_SECURITY, 0, 0), url)
        self.client.set((self.client.OBJ_SECURITY, 0, 1), self.bootstrap)
        self.client.set((self.client.OBJ_SECURITY, 0, 2), security_mode)

        # Set the PSK if we're using one
        if security_mode == canvas_net.Lwm2m.SECURITY_PSK:
            self.client.set((self.client.OBJ_SECURITY, 0, 3), psk_id)
            self.client.set((self.client.OBJ_SECURITY, 0, 5), psk)

        # If not bootstrap, need to create the server object instance
        if self.bootstrap == 0:
            self.client.set((self.client.OBJ_SECURITY, 0, 10), 101)
            self.client.create((self.client.OBJ_SERVER, 0))
            self.client.set((self.client.OBJ_SERVER, 0, 0), 101)
            self.client.set((self.client.OBJ_SERVER, 0, 1), reg_update_time)

        # Set up the device object
        self.client.create((self.client.OBJ_DEVICE, 0, 0), 32)
        self.client.set((self.client.OBJ_DEVICE, 0, 0), "Ezurio")
        self.client.create((self.client.OBJ_DEVICE, 0, 3), 32)
        self.client.set((self.client.OBJ_DEVICE, 0, 3), os.uname().release)
        self.client.create((self.client.OBJ_DEVICE, 0, 17), 32)
        self.client.set((self.client.OBJ_DEVICE, 0, 17), os.uname().machine)
        self.client.set_exec_handler(
            (self.client.OBJ_DEVICE, 0, 4), self.reboot_exec_cb)

    def restart_timer_cb(self, data):
        print("Restart LwM2M client")
        self.start()

    def watchdog_timer_cb(self, data):
        # Stop the watchdog timer
        if self.watchdog_timer is not None:
            self.watchdog_timer.stop()

        # If the watchdog expires, stop the client and restart it later
        print("LwM2M watchdog expired")
        self.client.stop(False)
        if self.restart_timer is None:
            self.restart_timer = canvas.Timer(
                LWM2M_RETRY_PERIOD, False, self.restart_timer_cb, None)
        self.restart_timer.start()

    def event_cb(self, evt):
        print("LwM2M event: {}".format(LwM2MClient.EVENTS[evt]))

        # On disconnect or error, stop the client and restart it later
        if evt == self.client.EV_RD_DISCONNECT or evt == self.client.EV_RD_NETWORK_ERROR:
            # Treat this the same as the watchdog expiration
            self.watchdog_timer_cb(None)

        # On registration/registration update, reset the watchdog
        elif evt == self.client.EV_RD_REGISTRATION_COMPLETE or evt == self.client.EV_RD_REG_UPDATE_COMPLETE:
            reg_update_time = self.client.get_int(
                (self.client.OBJ_SERVER, 0, 1))
            if reg_update_time is None or reg_update_time < 60:
                reg_update_time = 60

            # Watchdog for twice the registration update time, in milliseconds
            reg_update_time *= 2 * 1000

            if self.watchdog_timer is not None:
                self.watchdog_timer.change_period(reg_update_time)
            else:
                self.watchdog_timer = canvas.Timer(
                    reg_update_time, False, self.watchdog_timer_cb, None)

    def reboot_exec_cb(self, evt):
        self.client.stop(True)
        print("Rebooting in 2 seconds...")
        time.sleep(2)
        machine.reset()

    def start(self):
        if self.client is not None:
            self.client.start(self.bootstrap != 0)

    def stop(self, dereg: bool):
        if self.client is not None:
            self.client.stop(dereg)


class SntpClient:
    def __init__(self, config):
        self.timer = None
        self.sntp = None

        # Save the configuration
        self.hostname = config.get("sntp_hostname")
        self.period = config.get("sntp_period")
        if self.period is None:
            self.period = 3600

        # Create the SNTP client
        if self.hostname is None:
            # Use default SNTP server
            self.sntp = sntp.Sntp()
        else:
            # Use specified SNTP server
            self.sntp = sntp.Sntp(host=self.hostname)

        # Initial poll
        self.poll(None)

    def poll(self, data):
        try:
            self.sntp.poll()
        except Exception as e:
            print("SNTP poll failed:", e)
        if self.timer is None:
            self.timer = canvas.Timer(
                self.period * 1000, True, self.poll, None)
        self.timer.start()


class Scanner:
    def __init__(self):
        canvas_ble.init()
        self.scanner = canvas_ble.Scanner(scan_cb)
        self.scanner.set_phys(canvas_ble.PHY_1M)
        self.scanner.set_timing(100, 80)
        self.scanner.filter_add(self.scanner.FILTER_MANUF_DATA,
                                bytes([0x77, 0x00, 0xc9, 0x00]))

    def start(self):
        print("Scanner starting")
        self.scanner.start(True)

    def stop(self):
        self.scanner.stop()


def stop():
    # Stop any asynchronous tasks
    if client is not None:
        client.stop()
    if scanner is not None:
        scanner.stop()
    if lwm2m_client is not None:
        lwm2m_client.stop(True)


# Load configuration
config = config.Config()
config.load()
print("Configuration loaded")

# Wait for network to come up
print("Waiting for network")
net = NetHelper(None)
net.wait_for_ready()

# Instantiate the MQTT client
try:
    client = MqttClient(config)
except:
    print("MQTT client configuration is invalid")
    raise

# Instantiate the LwM2M client
try:
    lwm2m_client = LwM2MClient(config)
except:
    print("LwM2M client configuration is invalid")
    raise

# Instantiate the SNTP client
try:
    sntp_client = SntpClient(config)
except:
    print("SNTP client configuration is invalid")
    raise

# Start the LwM2M client
lwm2m_client.start()

# Instantiate the BLE scanner
scanner = Scanner()
scanner.start()
