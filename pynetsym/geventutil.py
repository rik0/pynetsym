import itertools


class SequenceAsyncResult(object):
    def __init__(self, seq):
        self.seq = seq

    def ready(self):
        return all(value.ready() for value in self.seq)

    def get(self):
        try:
            return [value.get() for value in self.seq]
        except Exception as e:
            import gevent
            print "xxx", gevent.getcurrent()
            raise e

    def flatten(self):
        items = self.get()
        return list(itertools.chain.from_iterable(items))
