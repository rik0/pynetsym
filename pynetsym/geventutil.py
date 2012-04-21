class SequenceAsyncResult(object):
    def __init__(self, seq):
        self.seq = seq

    def ready(self):
        return all(value.ready() for value in self.seq)

    def get(self):
        return [value.get() for value in self.seq]