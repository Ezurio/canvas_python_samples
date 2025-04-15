import canvas_uwb

print("Updating antenna calibration...")

# Initialize the UWB radio
canvas_uwb.init()

# NOTE: The radio will go back into DPD mode after 500 milliseconds of inactivity, so the following
# commands need to be executed immediately after initializing the radio

# Send a raw UCI command to set the Channel 5 ANTENNA_DELAY trim value
UWB_Set_Trim_ANTENNA_DELAY_5 = [0x2E, 0x26, 0x00, 0x06,
    0x01,
    0x02, 0x03,
    0x05, # Channel 5
    0x1D, 0x00  # 
    ]
	
# Send a raw UCI command to set the Channel 9 ANTENNA_DELAY trim value	
UWB_Set_Trim_ANTENNA_DELAY_9 = [0x2E, 0x26, 0x00, 0x06,
    0x01,
    0x02, 0x03,
    0x09, # Channel 9
    0x09, 0x00  # 
    ]	
		
canvas_uwb.raw_uci_send(bytes(UWB_Set_Trim_ANTENNA_DELAY_5))
canvas_uwb.raw_uci_send(bytes(UWB_Set_Trim_ANTENNA_DELAY_9))
print("Calibration update is complete.")

# Include this line to get line return for last command

