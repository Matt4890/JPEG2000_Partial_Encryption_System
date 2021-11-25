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
with open(sys.argv[2], 'rb') as fh:
  iv_sz_b = int.from_bytes(fh.read(4), 'little')
  iv = fh.read(iv_sz_b)
  key_sz_b = int.from_bytes(fh.read(4), 'little')
  key = fh.read(key_sz_b)

print('\nDECRYPT:')
seed = int.from_bytes(key, 'little')
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

eb = BytesIO()
prev = b'\x00' * 16
random.seed(seed)
for bl, i in [(bool(random.getrandbits(1)), i) for i in range(wav.data_sz_b // 16)]:
  pos = i*16
  if (bl):
    decryptor = cipher.decryptor()
    ct = wav.data_b[pos:pos+16]
    ptc = decryptor.update(ct) + decryptor.finalize()
    pt = bytes([_a ^ _b for _a, _b in zip(ptc, prev)]) 
    prev = ct
    eb.write(pt)
  else:
    eb.write(wav.data_b[pos:pos+16])
eb.write(wav.data_b[((wav.data_sz_b // 16) * 16):])

print('\nSAVE:')
wav.save(f'pdec-output.wav', eb.getvalue())