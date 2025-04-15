# Canvas BT510 Beacon Example
# Use the 'eddystone_tlm' python module to create
# and advertise an Eddystone beacon with TLM data
import canvas_ble as ble
from canvas import Timer
from board import Board
from power import Power
from temperature import TemperatureSensor
from eddystone_tlm import Eddystone_TLM
from open_close import OpenCloseSensor

app_id = "bt510_eddystone_tlm"
app_ver = "0.1.1"

def connection_cb(conn):
    pass

def disconnection_cb(conn):
    global advert
    # Restart advertising
    advert.start()

# Converts signed hundredths of degrees Celsius to 8.8 fixed-point representation.
def celsius_to_fixed_point(celsius_hundredths):
    whole_degrees = celsius_hundredths // 100 # range -128 to 127
    fractional_degrees = ((celsius_hundredths - (whole_degrees * 100))*256) // 100 # 256 levels in the range range 0 to 99
    return whole_degrees | (fractional_degrees << 8)

eddystone_tlm = None

# Update the beacon with current temperature and battery data
def update_beacon(data):
    global advert
    global temperature
    global eddystone_tlm
    encrypted = False

    advert.clear_buffer(False)
    advert.add_tag_string(ble.AD_TYPE_NAME_COMPLETE, "Canvas", False)
    temperature_degc_x100 = temperature.get_temperature_degc_x100()
    battery_mv = Power.get_battery_voltage_mv()
    if eddystone_tlm is None:
        eddystone_tlm = Eddystone_TLM(encrypted, battery_mv, celsius_to_fixed_point(temperature_degc_x100))
    else:
        eddystone_tlm.update(battery_mv, celsius_to_fixed_point(temperature_degc_x100))
    data = bytes(eddystone_tlm.get_beacon())
    advert.add_data(data, False)

    # Setup a simple manufacturer specific data element with the state of the open/close sensor
    company_id = 0x0077 # Set company ID to 0x0077 (Ezurio)
    protocol_id = 0x01  # Add a protocol ID, indicates a single byte of open/close data
    door_is_open = 1 if open_close.is_open() else 0 # 0x00 = closed, 0x01 = open
    data = bytes([ company_id & 0xFF, company_id >> 8, protocol_id, door_is_open ])
    advert.add_ltv(ble.AD_TYPE_MANU_SPECIFIC, data, False)
    advert.update()

# Initialize the BT510 board (temperature and open/close sensors)
board = Board()
temperature = TemperatureSensor()
temperature.enable()
open_close = OpenCloseSensor()
open_close.enable()

# Initialize the BLE module and setup the advertiser object
ble.init()
ble.set_periph_callbacks(connection_cb, disconnection_cb)
ble.set_tx_power(0)
advert = ble.Advertiser()
advert.stop()
advert.set_properties(False, False, True)

advert.set_phys(ble.PHY_CODED, ble.PHY_CODED)
#advert.set_phys(ble.PHY_1M, ble.PHY_1M)
advert.set_interval(100, 105)

# Create an Eddystone TLM beacon with temperature and battery voltage
update_beacon(None)

# Start advertising
advert.start()

# Setup a timer to periodically update the advertising data
# This will update temperature and battery voltage in the Eddystone TLM beacon
timer = Timer(1000, True, update_beacon, None)
timer.start()
