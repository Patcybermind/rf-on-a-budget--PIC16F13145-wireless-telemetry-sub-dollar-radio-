#!/usr/bin/env python3
"""
RTL-SDR Power Monitor - Fixed Timing Version
Should output 32 lines per second, 1 char per 1/32s
Also writes binary data to test.txt (1 for #, 0 for _)
"""

import numpy as np
import time
import sys
from rtlsdr import RtlSdr

def main():
    frequency = 95.65e6
    sample_rate = 2.048e6
    gain = 10
    update_interval = 1 / 256
    samples_per_read = int(sample_rate * update_interval * 0.95)  # Slightly reduced to avoid overrun

    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = frequency
        sdr.gain = gain

        print(f"RTL-SDR Power Monitor - {frequency/1e6:.2f} MHz")
        print("Power levels: 0=low, F=high")
        print("Writing binary data to test.txt\n")

        char_count = 0
        
        # Open file for writing, overriding any existing content
        with open('test.txt', 'w') as f:
            f.write('0: ')
            while True:
                loop_start = time.time()

                try:
                    samples = sdr.read_samples(samples_per_read)
                    power = np.mean(np.abs(samples)**2)
                    power_db = 10 * np.log10(power + 1e-10)

                    min_db = -15
                    max_db = 0
                    normalized = (power_db - min_db) / (max_db - min_db)
                    normalized = np.clip(normalized, 0, 1)

                    hex_value = int(normalized * 15)
                    hex_char = format(hex_value, 'X')
                    digital_char = '#' if hex_value > 9 else '_'

                    # Write to console
                    print(hex_char + digital_char, end='', flush=True)
                    
                    # Write binary data to file (1 for #, 0 for _)
                    binary_value = '1' if digital_char == '#' else '0'
                    f.write(binary_value)
                    f.flush()  # Ensure data is written immediately
                    
                    char_count += 1

                    if char_count >= 32:
                        print()
                        f.write('\n0: ')  # Add newline to file as well
                        char_count = 0

                except Exception as e:
                    print(f"\nError: {e}")
                    time.sleep(0.1)

                # Enforce consistent update rate
                elapsed = time.time() - loop_start
                sleep_time = update_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print("!", end='', flush=True)  # Mark dropped timing

    except Exception as e:
        print(f"Initialization error: {e}")
        sys.exit(1)
    finally:
        try:
            sdr.close()
        except:
            pass

if __name__ == "__main__":
    main()