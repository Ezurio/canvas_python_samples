from machine import Pin
import machine

class Board:
    
    def __init__(self):
        # Disconnect TM Pin
        Board.disconnect_pin(0, 3)
        # Disconnect ID pins
        Board.disconnect_pin(1, 1)
        Board.disconnect_pin(0, 2)
        Board.disconnect_pin(0, 25)
        # BATT_V and BATT_READ pins
        Board.disconnect_pin(0, 28)
        Board.disconnect_pin(1, 15)
        # Accelerometer interrupt pins
        Board.disconnect_pin(1, 5)
        Board.disconnect_pin(1, 12)

    @staticmethod
    def disconnect_pin(bank, idx):
        bank_str = "gpio@50000000"
        if bank > 0:
            bank_str = "gpio@50000300"
        return Pin((bank_str, idx), Pin.NO_CONNECT, Pin.PULL_NONE)
