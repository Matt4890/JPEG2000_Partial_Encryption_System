# Imports ---------------------------------------------------------------------------------------- #

import sys


# Globals ---------------------------------------------------------------------------------------- #

hex2bin = { '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
            '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111' }
bin2hex = { '0000': '0', '0001': '1', '0010': '2', '0011': '3', '0100': '4', '0101': '5', '0110': '6', '0111': '7',
            '1000': '8', '1001': '9', '1010': 'a', '1011': 'b', '1100': 'c', '1101': 'd', '1110': 'e', '1111': 'f' }

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
      print(pnum_len_b)
      pnum_len_b += 1
      pnum_len_ctr = 0
  
  if (last != None):
    pns = bin(last)[2:]
    sb += '0' * (pnum_len_b - len(pns))
    sb += pns

  padn = (8-(len(sb) % 8))
  sb += '1' + ('0' * (padn-1))
  return int(sb, 2).to_bytes(len(sb) // 8, 'big')

def lz_decode(data, patterns):
  bs = ''
  for c in data.hex(): bs += hex2bin[c]

  # print(f'    [LZD] {patterns}')
  inv_patterns = {v: k for (k, v) in patterns.items()}
  # print(f'    [LZD] {inv_patterns}')
  for k in inv_patterns.keys():
    buf = ''
    for c in inv_patterns[k]:
      buf += hex2bin[c]
    inv_patterns[k] = buf
  # print(f'    [LZD] {inv_patterns}')

  # Remove padding
  bs= bs[:bs.rfind('1')]

  dec = '' + bs[0:4]
  pnum_len_b = 1
  pnum_len_ctr = 0
  i = 4
  p = True
  while i < len(bs):
    if (p):
      # Include pattern
      pnum = int(bs[i:i+pnum_len_b], 2)
      dec += inv_patterns[pnum] if (pnum != 0) else ''
      i += pnum_len_b

      pnum_len_ctr += 1
      if ((pnum_len_b == 0) or (1 << (pnum_len_b - 1) <= pnum_len_ctr)): # 1 << n == 2**n
        pnum_len_b += 1
        pnum_len_ctr = 0
      p = False
    else:
      # Include symbol
      dec += bs[i:i+4]
      i += 4
      p = True
    # print(f'    [LZD] {"P" if not p else "S"} {dec}')

  # print(f'    [LZD] {len(dec)} {len(dec)%8}')
  return int(dec, 2).to_bytes(len(dec) // 8, 'big')

# Main ------------------------------------------------------------------------------------------- #

wav = WAV(sys.argv[1])
# patterns, last = lz_patterns(wav.data_b)
# enc = lz_encode(patterns, last)

print('\nENCODE:')

# ih = b'\x00\x00\x00\xB0\xBB'
ih = wav.data_b
print(ih.hex()[0:64])
print(ih.hex()[-64:])

patterns, last = lz_patterns(ih)
# print(patterns, last)

enc = lz_encode(patterns, last)
# print(enc)
# for c in enc.hex():
  # print(hex2bin[c], end='')
# print()

print('\nDECODE:')

dec = lz_decode(enc, patterns)
print(dec.hex()[0:64])
print(dec.hex()[-64:])

print(wav.data_b == dec)
