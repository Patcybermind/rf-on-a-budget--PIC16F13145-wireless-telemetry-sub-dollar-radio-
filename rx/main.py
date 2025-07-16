#!/usr/bin/env python3
"""
RTL-SDR Power Monitor for 95.65 MHz
Displays power levels as hexadecimal characters (0-F) in real-time
32 characters per line, updates every 1/32 second
"""

import numpy as np
import time
import sys
from rtlsdr import RtlSdr

def main():
    # Configuration
    frequency = 95.65e6  # 95.65 MHz
    sample_rate = 2.048e6  # 2.048 MHz sample rate
    gain = 0  # Automatic gain control
    update_interval = 1/32  # 1/32 second
    samples_per_read = int(sample_rate * update_interval)
    
    # Initialize RTL-SDR
    try:
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate
        sdr.center_freq = frequency
        sdr.gain = gain
        
        print(f"RTL-SDR Power Monitor - {frequency/1e6:.2f} MHz")
        print("Power levels: 0=lowest, F=highest")
        print("Press Ctrl+C to stop\n")
        
        char_count = 0
        
        while True:
            try:
                # Read samples from RTL-SDR
                samples = sdr.read_samples(samples_per_read)
                
                # Calculate power (magnitude squared)
                power = np.mean(np.abs(samples)**2)
                
                # Convert power to dB scale (with offset to avoid log(0))
                power_db = 10 * np.log10(power + 1e-10)
                
                # Normalize to 0-15 range (adjust these values based on your signal levels)
                # You may need to adjust min_db and max_db based on your environment
                min_db = -25  # Minimum expected power level
                max_db = -4 # Maximum expected power level
                
                normalized = (power_db - min_db) / (max_db - min_db)
                normalized = np.clip(normalized, 0, 1)  # Clamp to 0-1 range
                
                # Convert to hex character (0-F)
                hex_value = int(normalized * 15)
                hex_char = format(hex_value, 'X')
                if hex_value > 7:
                    digital_char = '#'  # Use '1' for values above 7
                else:
                    digital_char = '_'
                # Print character without newline
                print(hex_char + digital_char, end='', flush=True)
                char_count += 1
                
                # Start new line after 32 characters
                if char_count >= 32:
                    print()  # New line
                    char_count = 0
                
                # Wait for next update
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                print("\n\nStopping...")
                break
            except Exception as e:
                print(f"\nError reading samples: {e}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"Error initializing RTL-SDR: {e}")
        print("Make sure RTL-SDR is connected and rtl-sdr library is installed")
        sys.exit(1)
    
    finally:
        try:
            sdr.close()
        except:
            pass

if __name__ == "__main__":
    main()