# This is a generic sample that can be used on any platform with ADC peripheral support.
# It demonstrates how to configure ADC averaging (oversampling) and perform software averaging.
# It is recommended to adjust the defined values at the top of the file for your hardware setup.
# Refer to your platform's ADC peripheral documentation for supported configurations.

from machine import ADC
import time

ADC_CH = 1
# sample time is platform dependent, in nanoseconds. Not all values are supported.
ADC_SAMPLE_TIME = 40000
# Attenuate the voltage on the pin before conversion. 1, 2, 3, 4, 6 are typical options.
ADC_ATTENUATION = 4
# Multiply the voltage on the pin before conversion on the ADC input. 1, 2 are typical options.
ADC_GAIN = 1
# Resolution in bits. Be careful, more is not always better.
# The usable bits of the ADC depends on the platform.
# When using more bits, you may introduce more error because the bits are not usable.
ADC_RESOLUTION = 10
# ADC_BIT_SHIFT to convert to real resolution. This is only needed if using read_u16()
ADC_BIT_SHIFT = 16 - ADC_RESOLUTION
# 2^n samples averaged internally by ADC peripheral. One call to read_uv() or read_raw() returns the averaged result.
# Oversampling does averaging for you. You could skip the software averaging done below.
ADC_OVERSAMPLING = 0

# Total samples to collect and average in the app.
# Use oversampling and get rid of the loops below for better performance.
SAMPLE_COUNT = 2**4
# Time between samples in microseconds. This time is spent sleeping and not performing useful work.
SAMPLE_INTERVAL_US = 50

adc = ADC(ADC_CH)
adc.init(sample_ns=ADC_SAMPLE_TIME,
         atten=ADC_ATTENUATION,
         gain=ADC_GAIN,
         reference=adc.REF_INTERNAL,
         resolution=ADC_RESOLUTION,
         oversample=ADC_OVERSAMPLING)
# Get the reference voltage in volts for later calculations. Just use read_uv() and you don't need this :)
ADC_REF = adc.reference_uv() / 1000000  # V


def print_buffer_as_csv(buffer, should_round=False):
    csv_row = ''
    for i in range(len(buffer)):
        if should_round:
            csv_row += '{:.4f}'.format(buffer[i])  # format to 4 decimal places
        else:
            csv_row += str(buffer[i])
        if i < len(buffer)-1:
            csv_row += ','
    print(csv_row + '\n')


def sample():
    counts_buffer = []
    volts_buffer = []
    print('ADC reference: {} V, resolution: {}, oversampling: {}'.format(
        ADC_REF, ADC_RESOLUTION, ADC_OVERSAMPLING))

    for _ in range(SAMPLE_COUNT):
        # Read the ADC value as a normalized 16-bit value and convert to actual resolution
        # Uncomment this line to test this and comment out the read_raw() line below
        # counts = int(adc.read_u16() / (2 ** ADC_BIT_SHIFT))
        # Or read the ADC value directly at the configured resolution
        counts = adc.read_raw()
        counts_buffer.append(counts)

        # read_uv API does all the math for us. Recommended to use this.
        # Reading the raw counts and doing the math manually is just for demonstration.
        volts = adc.read_uv() / 1000000  # V
        volts_buffer.append(volts)

        time.sleep_us(SAMPLE_INTERVAL_US)

    # Reminder, this is just for demonstration purposes.
    # In practice, using adc.read_uv() to get voltage directly will result in better performance.
    print('\n----- {} SAMPLES (counts) -----\n'.format(SAMPLE_COUNT))
    print_buffer_as_csv(counts_buffer)
    print('---------------------------')
    avg_counts = sum(counts_buffer) / len(counts_buffer)
    print('Average ({}-bit counts): {:.0f}'.format(ADC_RESOLUTION, avg_counts))
    print('Average ({}-bit V) {:.4f}'.format(ADC_RESOLUTION, avg_counts *
          ADC_REF / (2**ADC_RESOLUTION) * ADC_ATTENUATION / ADC_GAIN))

    # Way less math to average the voltage readings directly
    print('\n----- {} SAMPLES (volts) -----\n'.format(SAMPLE_COUNT))
    print_buffer_as_csv(volts_buffer, True)
    print('---------------------------')
    avg_volts = sum(volts_buffer) / len(volts_buffer)
    print('Average (V): {:.4f}'.format(avg_volts))

    del counts_buffer
    del volts_buffer


sample()
