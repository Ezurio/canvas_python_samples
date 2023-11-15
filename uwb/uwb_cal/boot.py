import led_strip

# Turn on the red LED at boot
boot_led_strip = led_strip.led_strip("", 1)
boot_led_strip.set(0, 0x0f0000)
