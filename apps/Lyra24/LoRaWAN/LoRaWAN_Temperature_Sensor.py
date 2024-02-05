import time
import canvas
from machine import uart
import binascii
from TempAndHumClick import TempAndHumClick18

# Set the application key.309D9C17C9990D01E36B9751415AC73C
set_app_key = "AT%S 500=\"B6A4FEBCF91888CB3040F58CBDCBC404\"\r\n"

# Set the device EUI.
set_dev_eui = "AT%S 501=\"0025FF0A00FFFFFF\"\r\n"

# Set the join EUI.
set_join_eui = "AT%S 502=\"00250C0000FFFFFF\"\r\n"

# Set the region (3 = US)
set_lorawan_region = "ATS 611=3\r\n"

#Set no low power
set_lorawan_lp = "ATS 213=250\r\n"

# Set sub-band
set_lorawan_subband = "ATS 617=2\r\n"

# Save paramters to flash
save_rm126x_params = "AT&W\r\n"

# Reset
reset_rm126x = "ATZ\r\n"

# Join - Wait for asynchronous "CONNECT" message to know join the join accept was received by the end device.
lorawan_join = "AT+JOIN\r\n"

# Drop
lorawan_drop = "AT+DROP\r\n"

# SEND (The RM126x defaults to confirmed uplink packets. This can be changed via AT command if desired)
lorawan_send_uplink_start = "AT+SEND \""
lorawan_send_uplink_end = "\"\r\n"

# Get HW and SW Versions
lorawan_show_hw_variant = "ATI\r\n"
lorawan_show_fw_version = "ATI 3\r\n"

i2c_setup = ("I2C0", 'PD03', 'PD02')

#RS1XX Payload Fixed Parameters (Eventually all but Humidity Should be Variable)
rs1xx_msg_type = 0x01
rs1xx_opt = 0x00
rs1xx_frachum = 0x00
rs1xx_inthum = 0x00
rs1xx_battcap = 0x05
rs1xx_alarmmsg = 0x0000
rs1xx_backlogcnt = 0x0000

def temp_cb(event):
    temperature_f = th_click.get_temp_f()
    temp_split = divmod(temperature_f, 1)
    rs1xx_fmt_str = "%02X%02X%02X%02X%02X%02X%02X%04X%04X" %(rs1xx_msg_type, rs1xx_opt, rs1xx_frachum, rs1xx_inthum, int(temp_split[1] * 100), int(temp_split[0]), rs1xx_battcap, rs1xx_alarmmsg, rs1xx_backlogcnt)
    lorawan_uplink_payload = lorawan_send_uplink_start + rs1xx_fmt_str + lorawan_send_uplink_end
    print (lorawan_uplink_payload)
    uart1.write(lorawan_uplink_payload)
    temperature_timer.restart()
    
    return 0

def rx_read():
    read_len = 2
    while read_len > 0:
        uart_raw = uart1.read(128)
        if uart_raw is not None:
            read_len = len(uart_raw)
            print("LORAWAN IN: ", uart_raw)
        else:
           return 0
    return 0

def rx_cb(v: int):
    rx_read()
    return 0
#EUSART1 is the only available EUSART instance on the Lyra 24 hardware platform.
#Aux UART and SPI cannot coexist. They require the same pins on the Lyra24 hardware platform.
uart1_hw_config = ("EUSART1", "PB02", "PB01", "PB00", "PB03")
uart1 = uart(uart1_hw_config, rx_cb, 115200, False, 500, True, False, 1)
time.sleep(.5)
uart1.write(set_lorawan_region)
time.sleep(.5)
uart1.write(set_lorawan_subband)
time.sleep(.5)
uart1.write(set_lorawan_lp)
time.sleep(.5)
uart1.write(set_app_key)
time.sleep(.5)
uart1.write(set_dev_eui)
time.sleep(.5)
uart1.write(set_join_eui)
time.sleep(.5)
uart1.write(save_rm126x_params)
time.sleep(10)
uart1.write(reset_rm126x)
time.sleep(.5)
uart1.write(lorawan_show_hw_variant)
time.sleep(.5)
uart1.write(lorawan_show_fw_version)
time.sleep(.5)
uart1.write(lorawan_drop)
time.sleep(.5)
uart1.write(lorawan_join)
time.sleep(.5)

# Sensor Configuration
i2c_setup = ("I2C0", 'PD03', 'PD02')
th_click = TempAndHumClick18(i2c_setup)
th_click.set_resolution(14,14)

# Timer Setup for Triggering Readings.
event_data = 0
global temperature_timer
temperature_timer = canvas.Timer(60000, 0, temp_cb, event_data)
temperature_timer.start()
