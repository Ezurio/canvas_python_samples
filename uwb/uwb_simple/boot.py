import canvas

# Turn on the red LED at boot
boot_led_strip = canvas.LEDStrip("", 1)
boot_led_strip.set(0, 0x0f0000)
