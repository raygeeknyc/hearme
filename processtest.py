from multiprocessing import Process, Queue

def f(q):
    print "p2"
    q.put("two")

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    print q.get()
    p.join()
