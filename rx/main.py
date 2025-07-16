import numpy as np
from rtlsdr import RtlSdr

CENTER_FREQ = 95.65e6
SAMPLE_RATE = 2.4e6
BITRATE = 8  # bits per second
SAMPLES_PER_BIT = int(SAMPLE_RATE / BITRATE)

def envelope(samples):
    return np.abs(samples)

def smooth_signal(env, window_size=101):
    return np.convolve(env, np.ones(window_size)/window_size, mode='same')

def threshold_signal(env):
    env_smooth = smooth_signal(env)
    base_thresh = np.median(env_smooth)  # median more robust than mean
    thresh = base_thresh * 2 # was 2.5
    print(f"Threshold: {thresh:.5f} (median: {base_thresh:.5f})")
    return env_smooth > thresh

def find_edges(digital_signal):
    return np.where(np.diff(digital_signal.astype(int)) != 0)[0]

def decode_manchester(samples):
    env = envelope(samples)
    digital = threshold_signal(env)
    edges = find_edges(digital)
    
    bits = []
    i = 0
    half_bit_samples = SAMPLES_PER_BIT // 2

    # Filter out edges too close together (likely noise)
    filtered_edges = []
    for e in edges:
        if not filtered_edges or (e - filtered_edges[-1]) > half_bit_samples // 2:
            filtered_edges.append(e)
    edges = filtered_edges

    # Decode bits by checking transition direction on edges spaced by approx half bit
    while i < len(edges) - 1:
        interval = edges[i+1] - edges[i]
        if abs(interval - half_bit_samples) < half_bit_samples // 2:
            first_level = digital[edges[i]]
            second_level = digital[edges[i]+1]
            # Manchester: low->high = 1, high->low = 0
            if first_level == 0 and second_level == 1:
                bits.append(1)
            elif first_level == 1 and second_level == 0:
                bits.append(0)
            else:
                bits.append(None)
            i += 2
        else:
            i += 1

    print(f"Edges found: {len(edges)} Decoded bits: {len(bits)}")
    return bits

def bits_to_byte(bits):
    bits = bits[:8]
    if len(bits) < 8 or None in bits:
        return None
    val = 0
    for bit in bits:
        val = (val << 1) | bit
    return val

def main():
    sdr = RtlSdr()
    sdr.sample_rate = SAMPLE_RATE
    sdr.center_freq = CENTER_FREQ
    sdr.gain = 'auto'

    print(f"Listening at {CENTER_FREQ/1e6} MHz, {BITRATE} bps Manchester decoding")

    try:
        buffer_size = 262144  # chunk size
        bits_buffer = []

        while True:
            samples = sdr.read_samples(buffer_size)

            bits = decode_manchester(samples)
            bits_buffer.extend(bits)

            # Process bits in groups of 8
            while len(bits_buffer) >= 8:
                byte = bits_to_byte(bits_buffer[:8])
                if byte is not None:
                    print(f"Decoded byte: 0b{byte:08b} ({byte}) -----------------------")
                else:
                    print("Invalid bits:", bits_buffer[:8])
                bits_buffer = bits_buffer[8:]

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        sdr.close()

if __name__ == "__main__":
    main()


# test is 0b10110010;