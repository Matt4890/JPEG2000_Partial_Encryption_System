# Imports ---------------------------------------------------------------------------------------- #

from wav import WAV

import sys

# Functions -------------------------------------------------------------------------------------- #
 
# Source: http://rosettacode.org/wiki/LZW_compression#Python
def decompress(compressed):
  """Decompress a list of output ks to a string."""
  from io import BytesIO
 
  # Build the dictionary.
  dict_size = 256
  dictionary = {i: i.to_bytes(1, 'little') for i in range(dict_size)}
 
  # use BytesIO, otherwise this becomes O(N^2)
  # due to string concatenation in a loop
  result = BytesIO()
  w: bytes = b'' + (compressed.pop(0) % 256).to_bytes(1, 'little')
  result.write(w)
  for k in compressed:
    if k in dictionary:
      entry = dictionary[k]
    elif k == dict_size:
      entry = w + w[0].to_bytes(1, 'little')
    else:
      continue
    result.write(entry)
 
    # Add w+entry[0] to the dictionary.
    dictionary[dict_size] = w + entry[0].to_bytes(1, 'little')
    dict_size += 1
 
    w = entry
  return result.getvalue()

# Main ------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
  # Check args
  if (len(sys.argv) != 2):
    print('USAGE: python3 wav_decompressor.py file_to_decompress')
    exit(1)

  # Import
  print('READING...')
  cwav = WAV(sys.argv[1])
  cvals = [int.from_bytes(cwav.data_b[i:i+4], 'little') for i in range(0, cwav.data_sz_b, 4)]

  # Decompress
  print('DECODING...')
  dec = decompress(cvals)

  # Export
  print('SAVING...')
  cwav.save('output.wav', dec)
  exit(0)