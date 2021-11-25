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

  def save(self, filename, data):
    fh = open(filename, 'wb')

    fh.write(b'RIFF')
    fh.write((40 + len(data)).to_bytes(4, 'little'))
    fh.write(b'WAVE')

    fh.write(b'fmt ')
    fh.write(self.fmt_sz_b.to_bytes(4, 'little'))
    fh.write((1).to_bytes(2, 'little'))
    fh.write(self.num_ch.to_bytes(2, 'little'))
    fh.write(self.sample_rate.to_bytes(4, 'little'))
    fh.write(self.byte_rate.to_bytes(4, 'little'))
    fh.write(self.block_align.to_bytes(2, 'little'))
    fh.write(self.bps.to_bytes(2, 'little'))
    if (16 < self.fmt_sz_b): fh.write((0).to_bytes(self.fmt_sz_b - 16, 'little'))

    fh.write(b'data')
    fh.write(len(data).to_bytes(4, 'little'))
    fh.write(data)

    fh.close()

  def save_header(self, filename, data_sz_b):
    fh = open(filename, 'wb')

    fh.write(b'RIFF')
    fh.write((40 + data_sz_b).to_bytes(4, 'little'))
    fh.write(b'WAVE')

    fh.write(b'fmt ')
    fh.write(self.fmt_sz_b.to_bytes(4, 'little'))
    fh.write((1).to_bytes(2, 'little'))
    fh.write(self.num_ch.to_bytes(2, 'little'))
    fh.write(self.sample_rate.to_bytes(4, 'little'))
    fh.write(self.byte_rate.to_bytes(4, 'little'))
    fh.write(self.block_align.to_bytes(2, 'little'))
    fh.write(self.bps.to_bytes(2, 'little'))
    if (16 < self.fmt_sz_b): fh.write((0).to_bytes(self.fmt_sz_b - 16, 'little'))

    fh.write(b'data')
    fh.write(data_sz_b.to_bytes(4, 'little'))

    fh.close()