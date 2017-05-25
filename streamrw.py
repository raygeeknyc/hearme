import io
class StreamRW(io.BufferedRandom):
    def __init__(self, raw):
        super(StreamRW, self).__init__(raw)
        self.seek(0)

    def read(self, size=1):
        super(StreamRW, self).seek(self.read_offset)
        data = super(StreamRW, self).read(size)
        self.read_offset = self.tell()
        return data

    def write(self, data):
        super(StreamRW, self).seek(self.write_offset)
        written = super(StreamRW, self).write(data)
        self.write_offset = self.tell()
        return written

    def seek(self, offset):
        super(StreamRW, self).seek(offset)
        self.read_offset = self.write_offset = self.tell()
