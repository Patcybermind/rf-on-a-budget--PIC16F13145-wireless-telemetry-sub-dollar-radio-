#!/usr/bin/env python3
"""
RTL-SDR Manchester Decoder
Decodes Manchester-encoded OOK signals in real time
"""

import numpy as np
from rtlsdr import RtlSdr
import threading
import time
import queue
from collections import deque

class ManchesterDecoder:
    def __init__(self, sdr_freq=433.92e6, sample_rate=2.4e6, bitrate=8):
        self.sdr_freq = sdr_freq
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.samples_per_bit = int(sample_rate / bitrate)
        self.sync_pattern = 0b11111111  # 8 bits sync pattern
        
        # Initialize RTL-SDR
        self.sdr = RtlSdr()
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = sdr_freq
        self.sdr.gain = 'auto'
        
        # Processing parameters
        self.buffer_size = 4096
        self.detection_threshold = 0.1
        self.sample_buffer = deque(maxlen=self.samples_per_bit * 20)  # Buffer for ~20 bits
        self.bit_buffer = deque(maxlen=32)  # Buffer for bits
        
        # Threading
        self.running = False
        self.data_queue = queue.Queue()
        
    def start(self):
        """Start the decoder"""
        self.running = True
        self.sdr_thread = threading.Thread(target=self._sdr_reader)
        self.processing_thread = threading.Thread(target=self._signal_processor)
        
        self.sdr_thread.start()
        self.processing_thread.start()
        
        print(f"Manchester decoder started on {self.sdr_freq/1e6:.2f} MHz")
        print(f"Bitrate: {self.bitrate} bps, Sample rate: {self.sample_rate/1e6:.1f} MHz")
        print("Listening for sync pattern 0xFF...")
        
    def stop(self):
        """Stop the decoder"""
        self.running = False
        self.sdr.close()
        
    def _sdr_reader(self):
        """Read samples from RTL-SDR"""
        try:
            while self.running:
                samples = self.sdr.read_samples(self.buffer_size)
                if samples is not None:
                    self.data_queue.put(samples)
        except Exception as e:
            print(f"SDR reader error: {e}")
            
    def _signal_processor(self):
        """Process incoming samples"""
        while self.running:
            try:
                # Get samples from queue with timeout
                samples = self.data_queue.get(timeout=1.0)
                
                # Convert to magnitude (OOK detection)
                magnitude = np.abs(samples)
                
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
            bit_samples = list(self.sample_buffer)[:self.samples_per_bit]
            
            # Remove processed samples
            for _ in range(self.samples_per_bit):
                self.sample_buffer.popleft()
            
            # Determine bit value based on energy
            avg_energy = np.mean(bit_samples)
            bit_value = 1 if avg_energy > self.detection_threshold else 0
            
            # Add bit to buffer
            self.bit_buffer.append(bit_value)
            
            # Check for sync pattern and decode
            self._check_for_sync()
            
    def _check_for_sync(self):
        """Check for sync pattern and decode following data"""
        if len(self.bit_buffer) < 16:  # Need at least sync + some data
            return
            
        # Look for sync pattern in Manchester encoding
        # 0xFF in Manchester: 1010101010101010 (each bit becomes 10 for 1, 01 for 0)
        sync_manchester = self._encode_manchester([1,1,1,1,1,1,1,1])
        
        # Convert bit buffer to list for easier processing
        bits = list(self.bit_buffer)
        
        # Search for sync pattern
        for i in range(len(bits) - len(sync_manchester) + 1):
            if bits[i:i+len(sync_manchester)] == sync_manchester:
                print(f"Sync found at position {i}")
                
                # Extract data after sync
                data_start = i + len(sync_manchester)
                if data_start + 16 <= len(bits):  # Need 16 bits for one data byte
                    data_bits = bits[data_start:data_start+16]
                    decoded_byte = self._decode_manchester(data_bits)
                    
                    if decoded_byte is not None:
                        print(f"Decoded byte: 0x{decoded_byte:02X} ({decoded_byte})")
                        
                        # Clear processed bits
                        for _ in range(data_start + 16):
                            if self.bit_buffer:
                                self.bit_buffer.popleft()
                        return
                        
        # Keep only recent bits to prevent buffer overflow
        if len(self.bit_buffer) > 24:
            self.bit_buffer.popleft()
            
    def _encode_manchester(self, data_bits):
        """Encode bits using Manchester encoding (1 -> 10, 0 -> 01)"""
        encoded = []
        for bit in data_bits:
            if bit == 1:
                encoded.extend([1, 0])
            else:
                encoded.extend([0, 1])
        return encoded
        
    def _decode_manchester(self, manchester_bits):
        """Decode Manchester encoded bits"""
        if len(manchester_bits) % 2 != 0:
            return None
            
        decoded = []
        for i in range(0, len(manchester_bits), 2):
            if i + 1 < len(manchester_bits):
                pair = manchester_bits[i:i+2]
                if pair == [1, 0]:
                    decoded.append(1)
                elif pair == [0, 1]:
                    decoded.append(0)
                else:
                    # Invalid Manchester encoding
                    return None
                    
        if len(decoded) == 8:
            # Convert bit list to byte
            byte_value = 0
            for bit in decoded:
                byte_value = (byte_value << 1) | bit
            return byte_value
            
        return None

def main():
    """Main function"""
    # Configuration
    FREQUENCY = 433.92e6  # Adjust to your frequency
    SAMPLE_RATE = 2.4e6   # 2.4 MHz sample rate
    BITRATE = 8           # 8 bits per second
    
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
        print("Make sure RTL-SDR is connected and pyrtlsdr is installed:")
        print("pip install pyrtlsdr")

if __name__ == "__main__":
    main()