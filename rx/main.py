#!/usr/bin/env python3
"""
RTL-SDR Manchester Decoder - Diagnostic Version
Decodes Manchester-encoded OOK signals in real time
"""

import numpy as np
import threading
import time
import queue
from collections import deque
import sys

try:
    from rtlsdr import RtlSdr
except ImportError:
    print("ERROR: pyrtlsdr not installed. Install with: pip install pyrtlsdr")
    sys.exit(1)

class ManchesterDecoder:
    def __init__(self, sdr_freq=433.92e6, sample_rate=2.4e6, bitrate=8):
        self.sdr_freq = sdr_freq
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.samples_per_bit = int(sample_rate / bitrate)
        self.sync_pattern = 0b11111111  # 8 bits sync pattern
        
        print(f"Samples per bit: {self.samples_per_bit}")
        
        # Initialize RTL-SDR
        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = sample_rate
            self.sdr.center_freq = sdr_freq
            self.sdr.gain = 'auto'
            print(f"RTL-SDR initialized: freq={sdr_freq/1e6:.2f}MHz, rate={sample_rate/1e6:.1f}MHz")
        except Exception as e:
            print(f"ERROR: Failed to initialize RTL-SDR: {e}")
            raise
        
        # Processing parameters
        self.buffer_size = 4096
        self.detection_threshold = 0.01  # Very low threshold initially
        self.sample_buffer = deque(maxlen=self.samples_per_bit * 50)
        self.bit_buffer = deque(maxlen=100)
        
        # Statistics
        self.sample_count = 0
        self.bit_count = 0
        self.energy_readings = deque(maxlen=100)
        self.last_stats_time = time.time()
        
        # Threading
        self.running = False
        self.data_queue = queue.Queue()
        
    def start(self):
        """Start the decoder"""
        self.running = True
        self.sdr_thread = threading.Thread(target=self._sdr_reader)
        self.processing_thread = threading.Thread(target=self._signal_processor)
        self.stats_thread = threading.Thread(target=self._stats_monitor)
        
        self.sdr_thread.daemon = True
        self.processing_thread.daemon = True
        self.stats_thread.daemon = True
        
        self.sdr_thread.start()
        self.processing_thread.start()
        self.stats_thread.start()
        
        print(f"Manchester decoder started on {self.sdr_freq/1e6:.2f} MHz")
        print(f"Bitrate: {self.bitrate} bps, Sample rate: {self.sample_rate/1e6:.1f} MHz")
        print("Listening for sync pattern 0xFF...")
        print("Press Ctrl+C to stop")
        
    def stop(self):
        """Stop the decoder"""
        self.running = False
        try:
            self.sdr.close()
        except:
            pass
        
    def _sdr_reader(self):
        """Read samples from RTL-SDR"""
        print("SDR reader thread started")
        try:
            while self.running:
                samples = self.sdr.read_samples(self.buffer_size)
                if samples is not None and len(samples) > 0:
                    self.data_queue.put(samples)
                    self.sample_count += len(samples)
        except Exception as e:
            print(f"SDR reader error: {e}")
            self.running = False
            
    def _signal_processor(self):
        """Process incoming samples"""
        print("Signal processor thread started")
        
        while self.running:
            try:
                # Get samples from queue with timeout
                samples = self.data_queue.get(timeout=1.0)
                
                # Convert to magnitude (OOK detection)
                magnitude = np.abs(samples)
                
                # Track energy statistics
                current_energy = np.mean(magnitude)
                max_energy = np.max(magnitude)
                self.energy_readings.append(current_energy)
                
                # Add to sample buffer
                self.sample_buffer.extend(magnitude)
                
                # Process available samples
                self._process_samples()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Signal processor error: {e}")
                
    def _process_samples(self):
        """Process samples to extract bits"""
        while len(self.sample_buffer) >= self.samples_per_bit:
            # Take samples for one bit period
            bit_samples = []
            for _ in range(self.samples_per_bit):
                if self.sample_buffer:
                    bit_samples.append(self.sample_buffer.popleft())
            
            if len(bit_samples) == 0:
                continue
                
            # Determine bit value based on energy
            avg_energy = np.mean(bit_samples)
            max_energy = np.max(bit_samples)
            
            # Adaptive threshold based on recent energy readings
            if len(self.energy_readings) > 10:
                recent_avg = np.mean(list(self.energy_readings)[-50:])
                recent_max = np.max(list(self.energy_readings)[-50:])
                adaptive_threshold = recent_avg + (recent_max - recent_avg) * 0.3
            else:
                adaptive_threshold = self.detection_threshold
                
            bit_value = 1 if avg_energy > adaptive_threshold else 0
            
            # Add bit to buffer
            self.bit_buffer.append(bit_value)
            self.bit_count += 1
            
            # Check for sync pattern and decode
            self._check_for_sync()
            
    def _check_for_sync(self):
        """Check for sync pattern and decode following data"""
        if len(self.bit_buffer) < 32:
            return
            
        # Convert bit buffer to list for easier processing
        bits = list(self.bit_buffer)
        
        # Look for sync pattern in Manchester encoding
        # 0xFF = 11111111 in YOUR encoding becomes: 0101010101010101
        # Your encoding: bit 0 → 1,0 and bit 1 → 0,1
        sync_manchester = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
        
        # Search for sync pattern
        for i in range(len(bits) - len(sync_manchester) + 1):
            if bits[i:i+len(sync_manchester)] == sync_manchester:
                print(f"SYNC FOUND at position {i}!")
                
                # Extract data after sync
                data_start = i + len(sync_manchester)
                if data_start + 16 <= len(bits):
                    data_bits = bits[data_start:data_start+16]
                    decoded_byte = self._decode_manchester(data_bits)
                    
                    if decoded_byte is not None:
                        print(f"DECODED BYTE: 0x{decoded_byte:02X} ({decoded_byte}) '{chr(decoded_byte) if 32 <= decoded_byte <= 126 else '?'}'")
                        
                        # Clear processed bits
                        for _ in range(data_start + 16):
                            if self.bit_buffer:
                                self.bit_buffer.popleft()
                        return
                        
        # Keep only recent bits to prevent buffer overflow
        if len(self.bit_buffer) > 80:
            self.bit_buffer.popleft()
            
    def _decode_manchester(self, manchester_bits):
        """Decode Manchester encoded bits (YOUR encoding: bit 0 → 1,0 and bit 1 → 0,1)"""
        if len(manchester_bits) != 16:
            return None
            
        decoded = []
        for i in range(0, len(manchester_bits), 2):
            if i + 1 < len(manchester_bits):
                pair = manchester_bits[i:i+2]
                if pair == [1, 0]:
                    decoded.append(0)  # Your encoding: 1,0 = bit 0
                elif pair == [0, 1]:
                    decoded.append(1)  # Your encoding: 0,1 = bit 1
                else:
                    return None
                    
        if len(decoded) == 8:
            byte_value = 0
            for bit in decoded:
                byte_value = (byte_value << 1) | bit
            return byte_value
            
        return None
        
    def _stats_monitor(self):
        """Monitor and display statistics"""
        while self.running:
            time.sleep(2)
            
            if len(self.energy_readings) > 0:
                current_avg = np.mean(list(self.energy_readings)[-25:])
                current_max = np.max(list(self.energy_readings)[-25:])
                current_min = np.min(list(self.energy_readings)[-25:])
                
                # Show recent bit pattern
                recent_bits = list(self.bit_buffer)[-20:] if len(self.bit_buffer) >= 20 else list(self.bit_buffer)
                bit_string = ''.join(map(str, recent_bits))
                
                print(f"Stats: Samples={self.sample_count}, Bits={self.bit_count}, "
                      f"Energy: avg={current_avg:.4f}, max={current_max:.4f}, min={current_min:.4f}")
                print(f"Recent bits: {bit_string}")
                print(f"Queue size: {self.data_queue.qsize()}")
                
                # Auto-adjust threshold suggestion
                if current_max > 0.001:  # If we're getting some signal
                    suggested_threshold = current_min + (current_max - current_min) * 0.3
                    print(f"Suggested threshold: {suggested_threshold:.4f} (current: {self.detection_threshold:.4f})")
                    
                    # Auto-adjust if the difference is significant
                    if abs(suggested_threshold - self.detection_threshold) > 0.001:
                        self.detection_threshold = suggested_threshold
                        print(f"Auto-adjusted threshold to: {self.detection_threshold:.4f}")
                
                print("-" * 50)

def main():
    """Main function"""
    # Configuration
    FREQUENCY = 95.65e6  # Adjust to your frequency
    SAMPLE_RATE = 2.4e6   # 2.4 MHz sample rate
    BITRATE = 8           # 8 bits per second
    
    print("RTL-SDR Manchester Decoder - Diagnostic Version")
    print("=" * 50)
    
    try:
        # Create and start decoder
        decoder = ManchesterDecoder(
            sdr_freq=FREQUENCY,
            sample_rate=SAMPLE_RATE,
            bitrate=BITRATE
        )
        
        decoder.start()
        
        # Keep running until interrupted
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping decoder...")
                decoder.stop()
                break
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure RTL-SDR is connected: lsusb | grep RTL")
        print("2. Install pyrtlsdr: pip install pyrtlsdr")
        print("3. Check if another program is using the RTL-SDR")
        print("4. Try running with sudo if you get permission errors")
        print("5. Verify your transmitter is working and on the correct frequency")

if __name__ == "__main__":
    main()