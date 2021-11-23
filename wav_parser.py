# Imports ---------------------------------------------------------------------------------------- #

import sys

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Classes ---------------------------------------------------------------------------------------- #

class WAV:

  def __init__(self, filename):
    self.filename = filename

    fh = open(filename, 'rb')

    assert fh.read(4) == b'RIFF'
    self.file_sz_b = 8 + int.from_bytes(fh.read(4), 'little')
    assert fh.read(4) == b'WAVE'

    assert fh.read(4) == b'fmt '
    self.fmt_sz_b = int.from_bytes(fh.read(4), 'little')
    assert fh.read(2) == int.to_bytes(1, 2, 'little') # 1 -> Not compressed
    self.num_ch = int.from_bytes(fh.read(2), 'little')
    self.sample_rate = int.from_bytes(fh.read(4), 'little')
    self.byte_rate = int.from_bytes(fh.read(4), 'little')
    self.block_align = int.from_bytes(fh.read(2), 'little')
    self.bps = int.from_bytes(fh.read(2), 'little')
    assert self.byte_rate == self.sample_rate * self.num_ch * self.bps / 8
    assert self.block_align == self.num_ch * self.bps / 8
    if (16 < self.fmt_sz_b): fh.read(self.fmt_sz_b - 16)

    assert fh.read(4) == b'data'
    self.data_sz_b = int.from_bytes(fh.read(4), 'little')
    self.data_b = fh.read()
    assert len(self.data_b) == self.data_sz_b

    fh.close()

    print(f'File:          {filename}')
    print(f'Size:          {self.file_sz_b}')
    print(f'Num. Channels: {self.num_ch}')
    print(f'Sample Rate:   {self.sample_rate}')
    print(f'Bits/Sample:   {self.bps}')

# Functions -------------------------------------------------------------------------------------- #

def lz_patterns(data):
  hd = data.hex()
  pnum = 1
  patterns = {hd[0]:1}
  buf = ''

  for c in hd[1:]:
    buf += c
    if (buf not in patterns):
      pnum += 1
      patterns[buf] = pnum
      buf = ''

  last = None if buf == '' else patterns[buf]
  
  return (patterns, last)

def lz_encode(patterns, last = None): # FIXME: Assumes in order
  hex2bin = { '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
              '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111' }
  
  pnum_len_b = 0
  pnum_len_ctr = 0

  sb = ''

  for p in patterns.keys():
    if (len(p) == 1):
      sb += '0' * pnum_len_b
    else:
      pns = bin(patterns[p[:-1]])[2:]
      sb += '0' * (pnum_len_b - len(pns))
      sb += pns
    sb += hex2bin[p[-1]]

    pnum_len_ctr += 1
    if ((pnum_len_b == 0) or (1 << (pnum_len_b - 1) <= pnum_len_ctr)): # 1 << n == 2**n
      pnum_len_b += 1
      pnum_len_ctr = 0
  
  if (last != None):
    pns = bin(last)[2:]
    sb += '0' * (pnum_len_b - len(pns))
    sb += pns

  padn = (8-(len(sb) % 8))
  sb += '1' + ('0' * (padn-1))
  return int(sb, 2).to_bytes(len(sb) // 8, 'big')

# Main ------------------------------------------------------------------------------------------- #

wav = WAV(sys.argv[1])
patterns, last = lz_patterns(wav.data_b)
enc = lz_encode(patterns, last)

print(len(wav.data_b))
print(len(enc))