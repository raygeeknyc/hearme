import io
buf = io.BufferedRandom(io.BytesIO())
buf.write("a")
buf.flush()
a = buf.read(1024)
while True:
    print "reading"
    if not a: break
    print "read: {}".format(a)
buf.close()
