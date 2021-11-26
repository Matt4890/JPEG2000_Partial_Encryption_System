# Imports ---------------------------------------------------------------------------------------- #

from wav import WAV

import sys

# Functions -------------------------------------------------------------------------------------- #

# Source: http://rosettacode.org/wiki/LZW_compression#Python
def compress(uncompressed):
  """Compress a string to a list of output symbols."""
 
  # Build the dictionary.
  dict_size = 256
  dictionary = {i.to_bytes(1, 'little'): i for i in range(dict_size)}
 
  w: bytes = b""
  result = []
  for c in uncompressed:
    c: bytes = c.to_bytes(1, 'little')
    wc: bytes = w + c
    if wc in dictionary:
      w = wc
    else:
      result.append(dictionary[w])
      # Add wc to the dictionary.
      dictionary[wc] = dict_size
      dict_size += 1
      w = c
 
  # Output the code for w.
  if w:
    result.append(dictionary[w])
  return result

# Main ------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
  # Check args
  if (len(sys.argv) != 2):
    print('USAGE: python3 wav_compressor.py file_to_compress')
    exit(1)

  # Import
  print('READING...')
  wav = WAV(sys.argv[1])

  # Compress
  print('ENCODING...')
  ih = wav.data_b
  enc = compress(ih)

  # Export
  print('SAVING...')
  comp_data = b''
  wav.save_header('comp-output.wav', len(enc)*4)
  with open('comp-output.wav', 'ab') as fh:
    for i in enc:
      fh.write(i.to_bytes(4, 'little'))
  exit(0)
