#####
# Raymond Blum <raygeeknyc@gmail.com>
# Licensed under GNU-GPL-3.0-or-later
#####
import io
from streamrw import StreamRW

buf = StreamRW(io.BytesIO())
wrote = buf.write(b"abcdefg")
wrote += buf.write(b"hijklm")
data = buf.read(-1)
wrote += buf.write(b"nopqrstuvwxy")
data += buf.read(-1)
wrote += buf.write(b"z")
data += buf.read(-1)
print "read: {}".format(data)
buf.close()
