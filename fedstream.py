#####
# Raymond Blum <raygeeknyc@gmail.com>
# Licensed under GNU-GPL-3.0-or-later
#####
import logging
import Queue
import sys

class FedStream(object):
    def __init__(self, source):
        # Create a thread-safe buffer of audio data
        self._buff = source
        self.closed = False

    def close(self):
        self.closed = True

    def read(self, chunk_size):
        data = None
        while not data and not self.closed:
            try:
                data = [self._buff.get(timeout=0.1)]
            except Queue.Empty:
                pass
        if not data:
            return

        # Now consume whatever other data's still buffered.
        while True:
            try:
                data.append(self._buff.get(block=False))
            except Queue.Empty:
                break

        if self.closed:
            return
        return b''.join(data)
