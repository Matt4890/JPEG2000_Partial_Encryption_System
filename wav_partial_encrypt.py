# Imports ---------------------------------------------------------------------------------------- #

from wav import WAV

import random
import sys
import os
from io import BytesIO
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Functions -------------------------------------------------------------------------------------- #

def penc_random(wav, cipher, n):
  """Randomly encrypt every block with an n% chance."""
  eb = BytesIO()
  prev = b'\x00' * 16
  for bl, i in [(bool(random.randrange(100) < n), i) for i in range(wav.data_sz_b // 16)]:
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
  return eb.getvalue()

def penc_gap_n(wav, cipher, n):
  """Encrypt blocks with an n byte gap between them."""
  eb = BytesIO()
  prev = b'\x00' * 16
  i = 0
  while i < (wav.data_sz_b - (n + 16)):
    eb.write(wav.data_b[i:i+n])

    encryptor = cipher.encryptor()
    pt = bytes([_a ^ _b for _a, _b in zip(wav.data_b[i+n:i+n+16], prev)]) 
    ct = encryptor.update(pt) + encryptor.finalize()
    eb.write(ct)
    prev = ct

    i += n + 16
  eb.write(wav.data_b[(wav.data_sz_b - (n + 16)):])
  return eb.getvalue()

def penc_first_n(wav, cipher, n):
  """Encrypt the first n blocks."""
  eb = BytesIO()
  encryptor = cipher.encryptor()
  ct = encryptor.update(wav.data_b[0:n*16]) + encryptor.finalize()
  eb.write(ct)
  eb.write(wav.data_b[n*16:])
  return eb.getvalue()

def penc_last_n(wav, cipher, n):
  """Encrypt the last n blocks."""
  eb = BytesIO()
  encryptor = cipher.encryptor()
  eb.write(wav.data_b[:-n*16])
  ct = encryptor.update(wav.data_b[-n*16:]) + encryptor.finalize()
  eb.write(ct)
  return eb.getvalue()

def penc_full(wav, cipher, n=0):
  """Encrypt the entire data segment."""
  eb = BytesIO()
  encryptor = cipher.encryptor()
  ct = encryptor.update(wav.data_b[0:((wav.data_sz_b // 16) * 16)]) + encryptor.finalize()
  eb.write(ct)
  eb.write(wav.data_b[((wav.data_sz_b // 16) * 16):])
  return eb.getvalue()

# Main ------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
  # Check args
  if ((len(sys.argv) not in [3, 4]) or
      (sys.argv[2].lower() not in ['random', 'gap', 'first', 'last', 'full']) or
      (sys.argv[2].lower() != 'full' and len(sys.argv) != 4)):
    print('USAGE: python3 wav_partial_encrypt.py file_to_encrypt mode arg')
    print('  Encrypts the data segment of a wave file using different modes.')
    print('  Block size is 16B.')
    print('  modes:')
    print('   random - (arg)% chance each block is encrypted.')
    print('   gap    - Encrypt blocks with gap of (arg) bytes between them.')
    print('   first  - Encrypt first (arg) blocks only.')
    print('   last   - Encrypt last (arg) blocks only.')
    print('   full   - Encrypt the whole data segment. (arg is ignored)')
    exit(1)

  # Import
  print('READING...')
  wav = WAV(sys.argv[1])
  mode = sys.argv[2].lower()
  n = None if (len(sys.argv) <= 3) or (mode == 'full') else int(sys.argv[3])
  if (mode in ['first', 'last']): assert (n * 16 <= wav.data_sz_b)

  # Prepare encryption
  print('ENCRYPTING...')
  key = os.urandom(32)
  seed = int.from_bytes(key, 'little')
  random.seed(seed)
  iv = os.urandom(16)
  cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

  # Encrypt with selected mode
  ms = {'random': penc_random, 'gap': penc_gap_n, 'first': penc_first_n, 'last': penc_last_n, 'full': penc_full}
  enc = ms[mode](wav, cipher, n)

  # Export
  print('SAVEING...')
  wav.save(f'penc-output-{mode if (mode == "full") else (mode + "-" + str(n))}.wav', enc)
  with open(f'penc-{mode if (mode == "full") else (mode + "-" + str(n))}.key', 'wb') as fh:
    fh.write(len(iv).to_bytes(4, 'little'))
    fh.write(iv)
    fh.write(len(key).to_bytes(4, 'little'))
    fh.write(key)
  exit(0)