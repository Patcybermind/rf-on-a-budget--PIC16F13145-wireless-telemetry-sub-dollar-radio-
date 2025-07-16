import numpy as np
from rtlsdr import RtlSdr

CENTER_FREQ = 95.65e6
SAMPLE_RATE = 2.4e6
BITRATE = 8
SAMPLES_PER_BIT = int(SAMPLE_RATE / BITRATE)
SYNC_PATTERN = [1, 0, 1, 1, 0, 0, 1, 0]  # 0b10110010

def envelope(samples):
    return np.abs(samples)

def smooth_signal(env, window_size=101):
    return np.convolve(env, np.ones(window_size)/window_size, mode='same')

def threshold_signal(env):
    env_smooth = smooth_signal(env)
    thresh = max(np.mean(env_smooth) * 3, 0.05)
    return env_smooth > thresh

def find_edges(digital_signal):
    return np.where(np.diff(digital_signal.astype(int)) != 0)[0]

def decode_manchester(samples):
    env = envelope(samples)
    digital = threshold_signal(env)
    edges = find_edges(digital)
    
    bits = []
    i = 0
    bit_samples = SAMPLES_PER_BIT

    while i < len(edges) - 1:
        interval = edges[i+1] - edges[i]
        if abs(interval - bit_samples//2) < bit_samples//4:
            first_level = digital[edges[i]]
            second_level = digital[edges[i]+1]
            if first_level == 0 and second_level == 1:
                bits.append(1)
            elif first_level == 1 and second_level == 0:
                bits.append(0)
            else:
                bits.append(None)
            i += 2
        else:
            i += 1

    return bits

def bits_to_byte(bits):
    if len(bits) != 8 or None in bits:
        return None
    val = 0
    for bit in bits:
        val = (val << 1) | bit
    return val

def find_sync_and_decode(bits):
    i = 0
    while i <= len(bits) - 16:
        if bits[i:i+8] == SYNC_PATTERN:
            payload = bits[i+8:i+16]
            byte = bits_to_byte(payload)
            if byte is not None:
                print(f"Decoded byte: 0b{byte:08b} ({byte})")
            i += 16
        else:
            i += 1

def main():
    sdr = RtlSdr()
    sdr.sample_rate = SAMPLE_RATE
    sdr.center_freq = CENTER_FREQ
    sdr.gain = 'auto'

    print(f"Listening at {CENTER_FREQ/1e6} MHz, {BITRATE} bps Manchester decoding with sync")

    try:
        buffer_size = 262144
        bits_buffer = []

        while True:
            samples = sdr.read_samples(buffer_size)
            bits = decode_manchester(samples)
            bits_buffer.extend(bits)

            # Search for sync pattern and decode immediately after
            find_sync_and_decode(bits_buffer)

            # Avoid growing buffer indefinitely
            if len(bits_buffer) > 2000:
                bits_buffer = bits_buffer[-2000:]

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        sdr.close()

if __name__ == "__main__":
    main()
