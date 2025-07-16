import re
from collections import Counter
import numpy as np

raw_data = """0_7_0_8#0_6_3_8#0_0_8#0_8#6_4_0_0_7_8#0_0_0_0_0_0_0_0_0_0_0_0_0_
7_0_7_0_3_5_0_7_0_7_0_5_3_0_7_8#0_0_7_0_8#0_7_0_0_7_7_0_0_0_0_0_
0_0_0_0_0_0_0_7_0_7_0_4_5_0_7_0_7_0_6_3_0_7_8#0_0_7_0_8#0_7_0_0_
7_7_0_0_0_0_0_0_0_0_0_0_0_0_0_7_0_3_6_0_7_0_7_0_5_4_0_7_0_7_7_0_
4_0_7_7_0_7_0_2_8#0_0_0_0_0_0_0_0_0_0_0_0_0_5_3_0_7_0_7_0_7_1_3_
6_0_7_0_7_6_0_5_0_7_8#0_7_0_3_8#0_0_0_0_0_0_0_0_0_0_0_0_0_2_2_6_
0_7_0_7_0_4_5_0_7_0_7_0_7_4_0_7_0_7_8#0_6_0_5_8#0_0_0_0_0_0_0_0_
0_0_0_0_2_0_7_0_7_0_7_0_3_5_0_7_0_7_0_8#3_0_7_0_7_8#0_5_0_6_8#0_
0_0_0_0_0_0_0_0_0_0_0_0_5_0_7_0_7_0_5_4_0_7_0_7_0_6_1_7_0_0_7_0_
7_6_2_0_0_7_8#0_0_0_0_0_0_0_0_0_0_0_0_2_0_0_1_0_3_0_0_0_0_0_0_1_
0_0_0_0_0_0_0_1_0_2_0_0_2_0_0_0_0_0_0_0_0_0_0_0_0_0_0_4_1_0_5_0_
6_0_6_0_2_4_0_5_0_3_1_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_
0_0_5_2_0_7_0_6_0_5_0_1_3_0_5_0_0_0_0_0_0_0_0_0_0_0_0_3_0_0_0_0_
0_0_0_0_0_0_0_0_0_9#5_3_A#0_A#0_9#2_6_8#0_A#0_9#8#0_5_0_6_5_0_4_
0_1_6_0_0_0_0_0_0_0_0_0_0_0_0_0_0_1_3_0_5_0_4_0_0_3_0_4_0_4_0_4_
0_0_4_0_4_4_0_1_0_4_5_0_0_0_0_0_0_0_0_0_0_0_0_0_0_4_0_4_0_4_0_0_
3_0_4_0_4_0_4_0_0_4_0_4_4_0_1_0_3_4_0_0_0_0_0_0_0_0_0_0_0_0_0_3_
0_4_0_5_0_2_1_0_4_0_4_0_5_3_A#0_0_C#0_F#F#C#8#0_F#F#0_0_0_0_0_0_
0_0_0_0_0_0_F#0_F#0_F#8#D#F#0_F#0_F#4_E#D#F#0_0_F#0_F#D#E#4_0_F#
F#0_0_0_0_0_0_0_0_0_0_0_0_0_F#0_F#B#A#F#0_F#0_F#8#D#F#0_F#F#0_0_
F#C#F#0_F#0_0_F#E#0_0_0_0_0_0_0_0_0_0_0_0_F#2_F#D#8#F#0_F#0_F#A#
B#F#0_F#F#0_5_E#E#F#0_F#0_0_F#C#0_0_0_0_0_0_0_0_0_0_0_0_0_F#C#9#
F#0_F#0_F#C#9#F#0_F#0_F#E#0_F#0_F#F#0_F#0_E#F#0_0_0_0_0_0_0_0_0_
0_0_0_F#0_F#0_F#5_E#E#3_F#0_F#0_F#C#F#0_0_F#0_F#E#D#7_0_F#F#0_0_
0_0_0_0_0_0_0_0_0_0_F#0_F#0_F#8#C#F#0_F#0_F#4_E#D#F#0_0_F#0_F#E#
E#5_0_F#F#0_0_0_0_0_0_0_0_0_0_0_0_0_F#0_F#5_E#D#6_F#0_F#0_F#C#9#
F#F#0_0_F#B#F#5_F#0_0_F#F#0_0_0_0_0_0_0_0_0_0_0_0_F#0_F#B#A#"""

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
