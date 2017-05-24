import io
import sys
s = io.BytesIO()
buf = io.BufferedRandom(s)
s.write("a")
a = s.getvalue()
print "read: {}".format(a)
