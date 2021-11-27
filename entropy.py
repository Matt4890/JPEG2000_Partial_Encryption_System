from wav import WAV
from collections import Counter
from scipy.stats import entropy

input = WAV("input.wav")
output = WAV("output.wav")

print()

ohex = output.data_b.hex()
ihex = input.data_b.hex()

ocounter = Counter(ohex)
icounter = Counter(ihex)

p_O = []
p_I = []

for h in ocounter:
    p = ocounter[h]/len(ohex)
    p_O.append(p)

for h in icounter:
    p = icounter[h]/len(ihex)
    p_I.append(p)


print(entropy(p_O, base=2))
print(entropy(p_I, base=2))

