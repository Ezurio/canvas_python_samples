import canvas

class RGB:
    def __init__(self):
        self.led_strip = canvas.LEDStrip("", 12)
        self.color = 0
        self.set(self.color)

    def set(self, color):
        self.color = color
        self.led_strip.set(0, self.color)
        # LED strip has "GRB" color order rather than "RGB"
        c = ((self.color & 0xFF0000) >> 8)
        c |= ((self.color & 0x00FF00) << 8)
        c |= (self.color & 0xFF)
        for i in range(1,11):
            self.led_strip.set(i, c)
