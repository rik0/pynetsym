import time

__author__ = 'enrico'

class Timer(object):
    def __init__(self, callback):
        self.callback = callback

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *_):
        self.end_time = time.time()
        self.callback(self)

def execution_printer(out):
    def callback(timer):
        elapsed_time = (timer.end_time - timer.start_time) * 1000
        print >> out, 'Execution required %s ms.' % elapsed_time
    return callback
