# Imports ---------------------------------------------------------------------------------------- #

from wav import WAV

import random
import sys
import secrets
import os
from io import BytesIO
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Functions -------------------------------------------------------------------------------------- #
 

# Main ------------------------------------------------------------------------------------------- #

print('\nREAD:')
wav = WAV(sys.argv[1])

print('\nENCRYPT:')
key = os.urandom(32)
seed = int.from_bytes(key, 'little')
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

eb = BytesIO()
prev = b'\x00' * 16
random.seed(seed)
for bl, i in [(bool(random.getrandbits(1)), i) for i in range(wav.data_sz_b // 16)]:
  pos = i*16
  if (bl):
    encryptor = cipher.encryptor()
    pt = bytes([_a ^ _b for _a, _b in zip(wav.data_b[pos:pos+16], prev)]) 
    ct = encryptor.update(pt) + encryptor.finalize()
    eb.write(ct)
    prev = ct
  else:
    eb.write(wav.data_b[pos:pos+16])
eb.write(wav.data_b[((wav.data_sz_b // 16) * 16):])

print('\nSAVE:')
wav.save(f'penc-output.wav', eb.getvalue())
with open('penc.key', 'wb') as fh:
  fh.write(len(iv).to_bytes(4, 'little'))
  fh.write(iv)
  fh.write(len(key).to_bytes(4, 'little'))
  fh.write(key)