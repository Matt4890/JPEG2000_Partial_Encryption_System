# Imports ---------------------------------------------------------------------------------------- #

from wav import WAV

import random
import sys
import secrets
import os
from io import BytesIO
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Functions -------------------------------------------------------------------------------------- #
 
def pdec_random(wav, cipher, n):
  """Randomly decrypt every block with an n% chance."""
  eb = BytesIO()
  prev = b'\x00' * 16
  for bl, i in [(bool(random.randrange(100) < n), i) for i in range(wav.data_sz_b // 16)]:
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
  return eb.getvalue()

def pdec_gap_n(wav, cipher, n):
  """Decrypt blocks with an n byte gap between them."""
  eb = BytesIO()
  prev = b'\x00' * 16
  i = 0
  while i < (wav.data_sz_b - (n + 16)):
    eb.write(wav.data_b[i:i+n])

    decryptor = cipher.decryptor()
    ct = wav.data_b[i+n:i+n+16]
    ptc = decryptor.update(ct) + decryptor.finalize()
    pt = bytes([_a ^ _b for _a, _b in zip(ptc, prev)]) 
    prev = ct
    eb.write(pt)

    i += n + 16
  eb.write(wav.data_b[(wav.data_sz_b - (n + 16)):])
  return eb.getvalue()

def pdec_first_n(wav, cipher, n):
  """Decrypt the first n blocks."""
  eb = BytesIO()
  decryptor = cipher.decryptor()
  pt = decryptor.update(wav.data_b[0:n]) + decryptor.finalize()
  eb.write(pt)
  eb.write(wav.data_b[n:])
  return eb.getvalue()

def pdec_last_n(wav, cipher, n):
  """Decrypt the last n blocks."""
  eb = BytesIO()
  decryptor = cipher.decryptor()
  eb.write(wav.data_b[:-n])
  pt = decryptor.update(wav.data_b[-n:]) + decryptor.finalize()
  eb.write(pt)
  return eb.getvalue()

def pdec_full(wav, cipher, n=0):
  """Decrypt the entire data segment."""
  eb = BytesIO()
  decryptor = cipher.decryptor()
  pt = decryptor.update(wav.data_b[0:((wav.data_sz_b // 16) * 16)]) + decryptor.finalize()
  eb.write(pt)
  eb.write(wav.data_b[((wav.data_sz_b // 16) * 16):])
  return eb.getvalue()

# Main ------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
  # Check args
  if ((len(sys.argv) not in [4, 5]) or
      (sys.argv[3].lower() not in ['random', 'gap', 'first', 'last', 'full']) or
      (sys.argv[3].lower() != 'full' and len(sys.argv) != 5)):
    print('USAGE: python3 wav_partial_decrypt.py file_to_decrypt iv_key_file mode arg')
    print('  Decrypts the data segment of a wave file using different modes.')
    print('  The decryption mode must match the encryption mode in order to work.')
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
  with open(sys.argv[2], 'rb') as fh:
    iv_sz_b = int.from_bytes(fh.read(4), 'little')
    iv = fh.read(iv_sz_b)
    key_sz_b = int.from_bytes(fh.read(4), 'little')
    key = fh.read(key_sz_b)
  mode = sys.argv[3].lower()
  n = None if (len(sys.argv) <= 4) or (mode == 'full') else int(sys.argv[4])
  if (mode in ['first', 'last']): assert (n % 16 == 0) and (n * 16 <= wav.data_sz_b)

  # Prepare decryption
  print('DECRYPTING...')
  seed = int.from_bytes(key, 'little')
  random.seed(seed)
  cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

  # Decrypt with selected mode
  ms = {'random': pdec_random, 'gap': pdec_gap_n, 'first': pdec_first_n, 'last': pdec_last_n, 'full': pdec_full}
  dec = ms[mode](wav, cipher, n)

  # Export
  print('SAVEING...')
  wav.save(f'pdec-output-{mode if (mode == "full") else (mode + "-" + str(n))}.wav', dec)
  exit(0)