"""This sample works with the MikroE OLED C Click board, which has a 0.96" 96x96 pixel OLED display with an SSD1331 controller.
This sample has been tested with the BL54L15 and BL54LM20A DVK boards with the OLED C Click connected to the mikrobus socket.
The sample initializes the display, fills it with black, and then draws some text in green and white.
"""

import time
from machine import Pin, SPI, I2C

FONT_5X7 = (
    b'\x00\x00\x00\x00\x00'  # space
    b'\x00\x00\x5f\x00\x00'  # !
    b'\x00\x07\x00\x07\x00'  # "
    b'\x14\x7f\x14\x7f\x14'  # #
    b'\x24\x2a\x7f\x2a\x12'  # $
    b'\x23\x13\x08\x64\x62'  # %
    b'\x36\x49\x55\x22\x50'  # &
    b'\x00\x05\x03\x00\x00'  # '
    b'\x00\x1c\x22\x41\x00'  # (
    b'\x00\x41\x22\x1c\x00'  # )
    b'\x14\x08\x3e\x08\x14'  # *
    b'\x08\x08\x3e\x08\x08'  # +
    b'\x00\x50\x30\x00\x00'  # ,
    b'\x08\x08\x08\x08\x08'  # -
    b'\x00\x60\x60\x00\x00'  # .
    b'\x20\x10\x08\x04\x02'  # /
    b'\x3e\x51\x49\x45\x3e'  # 0
    b'\x00\x42\x7f\x40\x00'  # 1
    b'\x42\x61\x51\x49\x46'  # 2
    b'\x21\x41\x45\x4b\x31'  # 3
    b'\x18\x14\x12\x7f\x10'  # 4
    b'\x27\x45\x45\x45\x39'  # 5
    b'\x3c\x4a\x49\x49\x30'  # 6
    b'\x01\x71\x09\x05\x03'  # 7
    b'\x36\x49\x49\x49\x36'  # 8
    b'\x06\x49\x49\x29\x1e'  # 9
    b'\x00\x36\x36\x00\x00'  # :
    b'\x00\x56\x36\x00\x00'  # ;
    b'\x08\x14\x22\x41\x00'  # <
    b'\x14\x14\x14\x14\x14'  # =
    b'\x00\x41\x22\x14\x08'  # >
    b'\x02\x01\x51\x09\x06'  # ?
    b'\x32\x49\x79\x41\x3e'  # @
    b'\x7e\x11\x11\x11\x7e'  # A
    b'\x7f\x49\x49\x49\x36'  # B
    b'\x3e\x41\x41\x41\x22'  # C
    b'\x7f\x41\x41\x22\x1c'  # D
    b'\x7f\x49\x49\x49\x41'  # E
    b'\x7f\x09\x09\x09\x01'  # F
    b'\x3e\x41\x49\x49\x7a'  # G
    b'\x7f\x08\x08\x08\x7f'  # H
    b'\x00\x41\x7f\x41\x00'  # I
    b'\x20\x40\x41\x3f\x01'  # J
    b'\x7f\x08\x14\x22\x41'  # K
    b'\x7f\x40\x40\x40\x40'  # L
    b'\x7f\x02\x0c\x02\x7f'  # M
    b'\x7f\x04\x08\x10\x7f'  # N
    b'\x3e\x41\x41\x41\x3e'  # O
    b'\x7f\x09\x09\x09\x06'  # P
    b'\x3e\x41\x51\x21\x5e'  # Q
    b'\x7f\x09\x19\x29\x46'  # R
    b'\x46\x49\x49\x49\x31'  # S
    b'\x01\x01\x7f\x01\x01'  # T
    b'\x3f\x40\x40\x40\x3f'  # U
    b'\x1f\x20\x40\x20\x1f'  # V
    b'\x3f\x40\x38\x40\x3f'  # W
    b'\x63\x14\x08\x14\x63'  # X
    b'\x07\x08\x70\x08\x07'  # Y
    b'\x61\x51\x49\x45\x43'  # Z
    b'\x00\x7f\x41\x41\x00'  # [
    b'\x02\x04\x08\x10\x20'  # backslash
    b'\x00\x41\x41\x7f\x00'  # ]
    b'\x04\x02\x01\x02\x04'  # ^
    b'\x40\x40\x40\x40\x40'  # _
    b'\x00\x01\x02\x04\x00'  # `
    b'\x20\x54\x54\x54\x78'  # a
    b'\x7f\x48\x44\x44\x38'  # b
    b'\x38\x44\x44\x44\x20'  # c
    b'\x38\x44\x44\x48\x7f'  # d
    b'\x38\x54\x54\x54\x18'  # e
    b'\x08\x7e\x09\x01\x02'  # f
    b'\x0c\x52\x52\x52\x3e'  # g
    b'\x7f\x08\x04\x04\x78'  # h
    b'\x00\x44\x7d\x40\x00'  # i
    b'\x20\x40\x44\x3d\x00'  # j
    b'\x7f\x10\x28\x44\x00'  # k
    b'\x00\x41\x7f\x40\x00'  # l
    b'\x7c\x04\x18\x04\x78'  # m
    b'\x7c\x08\x04\x04\x78'  # n
    b'\x38\x44\x44\x44\x38'  # o
    b'\x7c\x14\x14\x14\x08'  # p
    b'\x08\x14\x14\x18\x7c'  # q
    b'\x7c\x08\x04\x04\x08'  # r
    b'\x48\x54\x54\x54\x20'  # s
    b'\x04\x3f\x44\x40\x20'  # t
    b'\x3c\x40\x40\x20\x7c'  # u
    b'\x1c\x20\x40\x20\x1c'  # v
    b'\x3c\x40\x30\x40\x3c'  # w
    b'\x44\x28\x10\x28\x44'  # x
    b'\x0c\x50\x50\x50\x3c'  # y
    b'\x44\x64\x54\x4c\x44'  # z
    b'\x00\x08\x36\x41\x00'  # {
    b'\x00\x00\x7f\x00\x00'  # |
    b'\x00\x41\x36\x08\x00'  # }
    b'\x10\x08\x08\x10\x10'  # ~
)

COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_YELLOW = 0xFFE0
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F

_COL_OFFSET = 16
WIDTH = 96
HEIGHT = 96


class OledCClick:
    def __init__(self, spi, dc, rst, rw, en):
        self.spi = spi
        self.dc = dc
        self.rst = rst
        self.rw = rw
        self.en = en
        self.width = WIDTH
        self.height = HEIGHT
        self._init_display()

    def _init_display(self):
        self.spi.configure(8000000, 0, 0, SPI.MSB)
        self.dc.value(0)
        self.en.value(1)
        self.rw.value(0)
        time.sleep_ms(10)

        self.rst.value(1)
        time.sleep_ms(10)
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(10)

        self._cmd_data(0xFD, 0x12)
        self._cmd_data(0xFD, 0xB1)
        self._cmd(0xAE)
        self._cmd_data(0xB3, 0xF1)
        self._cmd_data(0xCA, 95)
        self._cmd_data(0xA0, 0x32)
        self._cmd_data(0xA1, 0x80)
        self._cmd_data(0xA2, 0x20)
        self._cmd_data(0xB5, 0x00)
        self._cmd_data(0xAB, 0x01)
        self._cmd_data(0xB1, 0x32)
        self._cmd_data(0xB4, 0xA0, 0xB5, 0x55)
        self._cmd_data(0xBB, 0x17)
        self._cmd_data(0xBE, 0x05)
        self._cmd_data(0xC1, 0xC8, 0x80, 0xC8)
        self._cmd_data(0xC7, 0x0F)
        self._cmd_data(0xB6, 0x01)
        self._cmd(0xA6)
        time.sleep_ms(200)
        self._cmd(0xAF)

    def _cmd(self, cmd):
        self.dc.value(0)
        self.spi.transceive(bytes([cmd]))

    def _data(self, data):
        self.dc.value(1)
        if isinstance(data, int):
            self.spi.transceive(bytes([data]))
        else:
            self.spi.transceive(data)

    def _cmd_data(self, cmd, *args):
        self._cmd(cmd)
        for d in args:
            self._data(d)

    def _set_window(self, x0, y0, x1, y1):
        self._cmd_data(0x15, x0 + _COL_OFFSET, x1 + _COL_OFFSET)
        self._cmd_data(0x75, y0, y1)
        self._cmd(0x5C)

    def fill(self, color=COLOR_BLACK):
        self._set_window(0, 0, self.width - 1, self.height - 1)
        hi = color >> 8
        lo = color & 0xFF
        buf = bytes([hi, lo] * 16)
        self.dc.value(1)
        for _ in range((self.width * self.height) // 16):
            self.spi.transceive(buf)

    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self._set_window(x, y, x, y)
            self.dc.value(1)
            self.spi.transceive(bytes([color >> 8, color & 0xFF]))

    def text(self, string, x, y, color=COLOR_WHITE, scale=1):
        for char in string:
            c = ord(char) - 32
            if c < 0 or c >= 95:
                c = 0
            for col in range(5):
                line = FONT_5X7[c * 5 + col]
                for row in range(7):
                    if line & (1 << row):
                        if scale == 1:
                            self.pixel(x + col, y + row, color)
                        else:
                            self._fill_rect(
                                x + col * scale,
                                y + row * scale,
                                scale, scale, color
                            )
            x += (5 + 1) * scale

    def _fill_rect(self, x, y, w, h, color):
        if x >= self.width or y >= self.height:
            return
        x1 = min(x + w - 1, self.width - 1)
        y1 = min(y + h - 1, self.height - 1)
        self._set_window(x, y, x1, y1)
        hi = color >> 8
        lo = color & 0xFF
        buf = bytes([hi, lo] * w)
        self.dc.value(1)
        for _ in range(y1 - y + 1):
            self.spi.transceive(buf)


# Example usage:
try:
    # Boards with the nPM1300 PMIC default to a 100mA VBUS current limit,
    # which is not sufficient for the OLED display.
    # Configure the PMIC to allow up to 500mA.
    pmic = I2C("mikrobus_i2c", 0x6B)
    pmic.write(bytes([0x02, 0x01, 0x05]))  # Set ILIM = 5 (500mA)
    pmic.write(bytes([0x02, 0x00, 0x01]))  # Trigger ILIMUPDATE
    # Read VBUS current limit register (base 0x02, offset 0x01)
    data = pmic.write_read(bytes([0x02, 0x01]), 1)
    data = data[0] & 0x0F # ILIM value is in the lower 4 bits
    print('ILIM register: {} = {}mA'.format(data, data * 100))
except Exception as e:
    print('Error configuring PMIC current', e)

print('Init IO')
cs = Pin("MB_CS", Pin.OUT, 0)
spi = SPI("mikrobus_spi", cs)
dc = Pin("MB_PWM", Pin.OUT, 0)
rst = Pin("MB_RST", Pin.OUT, 0)
rw = Pin("MB_AN", Pin.OUT, 0)
en = Pin("MB_INT", Pin.OUT, 0)

oled = OledCClick(spi, dc, rst, rw, en)
print('Fill screen black')
oled.fill()
msg = "Hello!"
print('Draw {}'.format(msg))
oled.text(msg, 10, 10, COLOR_GREEN)
msg = "OLED C"
print('Draw {}'.format(msg))
oled.text(msg, 10, 30, COLOR_WHITE, scale=2)
