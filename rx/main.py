import numpy as np
from rtlsdr import RtlSdr

CENTER_FREQ = 95.65e6
SAMPLE_RATE = 2.4e6
BITRATE = 8  # bits per second
SAMPLES_PER_BIT = int(SAMPLE_RATE / BITRATE)
SYNC_SEQ = [1,0,1,1,0,0,1,0]  # your sync sequence

def envelope(samples):
    return np.abs(samples)

def smooth_signal(env, window_size=101):
    return np.convolve(env, np.ones(window_size)/window_size, mode='same')

def threshold_signal(env):
    env_smooth = smooth_signal(env)
    base_thresh = np.mean(env_smooth)
    thresh = max(base_thresh * 3, 0.05)  # heuristic threshold
    # print(f"Threshold: {thresh:.4f} (mean: {base_thresh:.4f})")  # uncomment for debugging
    return env_smooth > thresh

def find_edges(digital_signal):
    edges = np.where(np.diff(digital_signal.astype(int)) != 0)[0]
    return edges

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

            # Manchester decoding (low->high = 1, high->low = 0)
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
    bits = bits[:8]
    if len(bits) < 8 or None in bits:
        return None
    val = 0
    for bit in bits:
        val = (val << 1) | bit
    return val

def find_sync(bits_buffer):
    for i in range(len(bits_buffer) - len(SYNC_SEQ) + 1):
        if bits_buffer[i:i+len(SYNC_SEQ)] == SYNC_SEQ:
            return i
    return -1

def main():
    sdr = RtlSdr()
    sdr.sample_rate = SAMPLE_RATE
    sdr.center_freq = CENTER_FREQ
    sdr.gain = 'auto'

    print(f"Listening at {CENTER_FREQ/1e6} MHz, {BITRATE} bps Manchester decoding with sync")

    bits_buffer = []
    synced = False
    buffer_size = 262144

    try:
        while True:
            samples = sdr.read_samples(buffer_size)
            bits = decode_manchester(samples)
            bits_buffer.extend(bits)

            if not synced:
                idx = find_sync(bits_buffer)
                if idx >= 0:
                    print(f"Sync found at bit index {idx}")
                    bits_buffer = bits_buffer[idx:]
                    synced = True
                else:
                    bits_buffer = bits_buffer[-len(SYNC_SEQ):]
                    continue

            while len(bits_buffer) >= 8:
                byte = bits_to_byte(bits_buffer[:8])
                if byte is not None:
                    print(f"Decoded byte: 0b{byte:08b} ({byte}) --------------------------------")
                else:
                    print("Invalid bits:", bits_buffer[:8])
                bits_buffer = bits_buffer[8:]

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        sdr.close()

if __name__ == "__main__":
    main()
