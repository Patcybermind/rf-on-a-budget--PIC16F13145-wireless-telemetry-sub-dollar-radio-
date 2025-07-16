import re
from collections import Counter
import numpy as np

raw_data = """0_C#D#4_0_D#A#0_A#B#3_0_C#A#9#4_0_!0_B#D#7_0_D#B#A#6_0_B#B#0_0_0_
C#E#C#A#0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_F#F#
0_B#F#B#0_F#F#0_B#F#B#0_F#D#0_A#D#7_0_C#A#0_8#B#5_0_B#A#8#6_0_0_
!9#D#9#0_D#C#A#7_0_9#A#3_0_0_9#E#C#A#3_0_0_0_0_0_0_0_0_0_0_0_0_0_"""

# Extract hexadecimal values
hex_samples = re.findall(r'([0-9A-F])[_#]', raw_data)
samples = [int(h, 16) for h in hex_samples]

# Estimate a good threshold using mode or average of most common values
hist = Counter(samples)
most_common = [val for val, _ in hist.most_common(3)]
threshold = int(np.mean(most_common))  # You could also try min+max//2 or clustering

# Convert to logic levels
logic = [1 if x >= threshold else 0 for x in samples]

# Manchester decode: 4 samples per bit, mid 2 determine the encoded bit
decoded = []
for i in range(0, len(logic) - 3, 4):
    mid1, mid2 = logic[i+1], logic[i+2]
    if mid1 == 1 and mid2 == 0:
        decoded.append(0)
    elif mid1 == 0 and mid2 == 1:
        decoded.append(1)
    else:
        decoded.append('E')  # Error case

# Print output
print("Threshold:", threshold)
print("First 64 decoded bits:", decoded[:64])
print("Errors:", decoded.count('E'), "out of", len(decoded))
