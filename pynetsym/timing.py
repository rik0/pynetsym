import time
import sys

__author__ = 'enrico'

def execution_printer(out):
    def callback(timer):
        elapsed_time = (timer.end_time - timer.start_time) * 1000
        print >> out, 'Execution required %s ms.' % elapsed_time
    return callback

class Timer(object):
    def __init__(self, callback=None):
        self.callback = callback

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *_):
        self.end_time = time.time()
        if callable(self.callback):
            self.callback(self)
