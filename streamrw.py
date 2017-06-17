import io
import logging

class StreamRW(io.BufferedRandom):
    def __init__(self, raw, buffer_size):
        super(StreamRW, self).__init__(raw, buffer_size)
        self.seek(0)

    def open(self):
        logging.debug("close RW Stream")
        self.read_offset = 0
        self.write_offset = 0
        super(StreamRW, self).open()
        
    def close(self):
        logging.debug("close RW Stream")
        super(StreamRW, self).close()

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
