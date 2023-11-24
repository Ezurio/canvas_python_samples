import canvas_ble as ble
import canvas
from TempAndHumClick import TempAndHumClick18
import time
import os

print("Temperature and Humidity Click 18 with GATT configuration")

# The connection
connection = None

# Transient control values
discon = False
temperature_notify_enabled = False
humidity_notify_enabled = False
temperature_previous = 0
humidity_previous = 0
event_data = {}

# Configuration
config = { }


def load_config():
    global config
    # Set default configuration values
    config["temperature_threshold"] = 1000
    config["humidity_threshold"] = 1000
    config["temperature_interval"] = 1000
    config["humidity_interval"] = 1000
    # Load configuration from a file
    try:
        f = open("th_gatt_config.cb", "rb")
    except:
        print("Configuration file not found, saving defaults")
        save_config()
        return
    # Read the entire file
    cbor = f.read()
    f.close()
    if cbor is None:
        print("Configuration file is empty, saving defaults")
        save_config()
        return
    # Convert CBOR to an object
    config_file = canvas.zcbor_to_obj(cbor)
    if config_file is None:
        print("Configuration is corrupt, saving defaults")
        save_config()
        return
    # Copy the configuration from the file
    for c in config_file:
        config[c] = config_file[c]

def save_config():
    global config
    config_file = { }
    # Copy config values from the live config object
    config_file["temperature_threshold"] = config["temperature_threshold"]
    config_file["humidity_threshold"] = config["humidity_threshold"]
    config_file["temperature_interval"] = config["temperature_interval"]
    config_file["humidity_interval"] = config["humidity_interval"]
    # Convert the configuration to CBOR
    cbor = canvas.zcbor_from_obj(config_file, 0)
    if cbor is None:
        print("Unable to convert configuration to CBOR")
        return
    # Write the CBOR to a file
    f = open("th_gatt_config.cb", "wb")
    if f is None:
        print("Unable to open configuration file")
        return
    size = f.write(cbor)
    f.close()


def cb_temp(event_object):
    global temperature_notify_enabled
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        print(event_object.name, " disabled")
        temperature_notify_enabled = False
    if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
        print(event_object.name, " enabled")
        temperature_notify_enabled = True


def cb_hum(event_object):
    global humidity_notify_enabled
    if event_object.type == ble.GattServer.EVENT_CCCD_NONE:
        print(event_object.name, " disabled")
        humidity_notify_enabled = False
    if event_object.type == ble.GattServer.EVENT_CCCD_NOTIFY:
        print(event_object.name, " enabled")
        humidity_notify_enabled = True


def cb_tempThresh(event_object):
    global config
    config["temperature_threshold"] = int.from_bytes(event_object.data, 'little')
    print("Temperature threshold now: ", config["temperature_threshold"])
    save_config()

def cb_humThresh(event_object):
    global config
    config["humidity_threshold"] = int.from_bytes(event_object.data, 'little')
    print("Humidity threshold now: ", config["humidity_threshold"])
    save_config()


def cb_tempInterval(event_object):
    global config
    global temperature_timer
    config["temperature_interval"] = int.from_bytes(event_object.data, 'little')
    temperature_timer.change_period(config["temperature_interval"])
    print("Temperature interval now: ", config["temperature_interval"])
    save_config()


def cb_humInterval(event_object):
    global config
    global humidity_timer
    config["humidity_interval"] = int.from_bytes(event_object.data, 'little')
    humidity_timer.change_period(config["humidity_interval"])
    print("Humidity interval now: ", config["humidity_interval"])
    save_config()


def cb_con(conn):
    global connection
    global discon
    connection = conn
    print("Connected: ", connection)
    discon = False


def cb_discon(conn):
    global advert
    global discon
    global connection
    print("Disconnected: ")
    discon = True
    connection = None
    advert.start()


def cb_tempSample(event):
    global my_gattserver
    global connection
    global config
    global th_click
    global temperature_notify_enabled
    global temperature_previous
    if connection == None or temperature_notify_enabled == False:
        return
    temperature = th_click.get_temp_c() * 1000
    diff=abs(temperature - temperature_previous)
    if diff > config["temperature_threshold"]:
        try:
            string = "Temperature: %d.%02d" %(temperature/1000, temperature%1000/10)
            value = bytes(string,'utf-8')
            my_gattserver.notify(connection, "Temp", value)
            temperature_previous = temperature
        except:
            print("Notify failed: ", temperature)


def cb_humSample(event):
    global my_gattserver
    global connection
    global config
    global th_click
    global humidity_notify_enabled
    global humidity_previous
    if connection == None or humidity_notify_enabled == False:
        return
    humidity = th_click.get_humidity() * 1000
    diff=abs(humidity - humidity_previous)
    if diff > config["humidity_threshold"]:
        try:
            string = "Humidity: %d.%d" %(humidity/1000, humidity%1000/10)
            value = bytes(string,'utf-8')
            my_gattserver.notify(connection, "Hum", value)
            humidity_previous = humidity
        except:
            print("Notify failed: ", humidity)


def start_ble():
    global advert
    global my_gattserver
    # Start an advert
    ble.init()
    print("Starting Advertiser")
    advert = ble.Advertiser()
    advert.stop()
    advert.clear_buffer(False)
    advert.add_ltv(1, b"\x06", False)
    advert.add_tag_string(9, "Canvas T&H Notify", False)
    advert.set_phys(ble.PHY_1M, ble.PHY_1M)
    advert.set_properties(True, False, False)
    advert.set_interval(200, 250)
    advert.start()
    print("Build Dictionary")
    ble.set_periph_callbacks(cb_con, cb_discon)
    my_gattserver = ble.GattServer()
    my_gattserver.build_from_dict(gatt_table)
    print("Starting GATT server")
    my_gattserver.start()
    my_gattserver.write("TempThresh", config["temperature_threshold"].to_bytes(4, 'little'))
    my_gattserver.write("HumThresh", config["humidity_threshold"].to_bytes(4, 'little'))
    my_gattserver.write("TempInterval", config["temperature_interval"].to_bytes(4, 'little'))
    my_gattserver.write("HumInterval", config["humidity_interval"].to_bytes(4, 'little'))
    print("GATT server started")


def start_sensor():
    global board
    global th_click
    board = os.uname().machine
    th_click = None
    if "LYRA_24" in board:
        i2c_setup = ("I2C0", 'PD03', 'PD02')
    else:
        ad0 = ("gpio@50000000", 31)
        ad1 = ("gpio@50000000", 20)
        i2c_setup = "i2c@40003000"
    th_click = TempAndHumClick18(i2c_setup)


def start_timers():
    global config
    global event_data
    global temperature_timer
    global humidity_timer
    print("Starting timers")
    temperature_timer = canvas.Timer(config["temperature_interval"], True, cb_tempSample, event_data)
    result = temperature_timer.start()
    humidity_timer = canvas.Timer(config["humidity_interval"], True, cb_humSample, event_data)
    result = humidity_timer.start()

#--------------------------------------
# Application script
#--------------------------------------
# GATT table definition
gatt_table = {
    "Service 1":{
        "Name": "Notifications",
        "UUID":"b8d00010-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1":{
            "Name": "Temp",
            "UUID" :"b8d00011-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Notify",
            "Callback" : cb_temp
        },
        "Characteristic 2":{
            "Name": "Hum",
            "UUID" :"b8d00012-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 20,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Notify",
            "Callback" : cb_hum
        }
    },
    "Service 2":{
        "Name": "Thresholds",
        "UUID":"b8d00020-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1": {
            "Name": "TempThresh",
            "UUID" :"b8d00021-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 4,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read Write",
            "Callback" : cb_tempThresh
        },
        "Characteristic 2": {
            "Name": "HumThresh",
            "UUID" :"b8d00022-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 4,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read Write",
            "Callback" : cb_humThresh
        }
    },
    "Service 3": {
        "Name": "Intervals",
        "UUID":"b8d00030-6329-ef96-8a4d-55b376d8b25a",
        "Characteristic 1": {
            "Name": "TempInterval",
            "UUID" :"b8d00031-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 4,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read Write",
            "Callback" : cb_tempInterval
        },
        "Characteristic 2": {
            "Name": "HumInterval",
            "UUID" :"b8d00032-6329-ef96-8a4d-55b376d8b25a",
            "Length" : 4,
            "Read Encryption" : "None",
            "Write Encryption" : "None",
            "Capability" : "Read Write",
            "Callback" : cb_humInterval
        }
    }
}

load_config()
start_sensor()
start_ble()
start_timers()
#--------------------------------------

