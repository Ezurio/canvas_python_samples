import time
from canvas import LEDStrip

# RGB colors of the rainbow
COLORS = [ 0x9400D3, 0x4B0082, 0x0000FF, 0x00FF00, 0xFFFF00, 0xFF7F00, 0xFF0000 ]

led = LEDStrip("", 1)

def fade(color_from, color_to, steps, delay):
    red = color_from >> 16
    red_step = ((red - (color_to >> 16))) // steps
    green = (color_from >> 8) & 0xFF
    green_step = ((green - ((color_to >> 8) & 0xFF))) // steps
    blue = color_from & 0xFF
    blue_step = (blue - ((color_to & 0xFF))) // steps
    for i in range(steps):
        color = (int(red) << 16) | (int(green) << 8) | int(blue)
        err = led.set(0, color)
        red = red - red_step
        green = green - green_step
        blue = blue - blue_step
        time.sleep_ms(delay)

i = 0
color = 0x000000
while True:
    fade(color, COLORS[i], 32, 5)
    color = COLORS[i]
    i = i + 1
    if i >= len(COLORS):
        i = 0
