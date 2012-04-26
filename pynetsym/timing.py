"""
This module deals with easy to use facilities to time execution.
"""

import time


class TimerStateError(AttributeError):
    """
    This is raised when attributes are called in a Timer when not
    in the appropriate state (i.e., it did not __enter__ in the block
    or it did not __exit__ depending on the actual attribute)
    """


class TimeLogger(object):

    """
    Timer callback to log execution times to a stream.
    """

    default_message = 'Execution required %s ms.\n'
    """Default log message"""

    def __init__(self, out, message=default_message):
        """
        Creates the TimeLogger object
        @param out: the stream where the event is logged
        @type out: file
        @param message: the message to log. It will be formatted passing
            it the value of the execution time. A newline is not inserted
            automatically: if that is the intended behavior, just add the
            line terminator to the end of the message.
        @type message: str
        """
        self.out = out
        self.message = message

    def __call__(self, timer):
        """
        TimerLogger are callable object that are called as callbacks
        when everithing is finished.
        @param timer: the timer object passes itself when done
        @type timer: Timer
        """
        self.out.write(self.message % timer.elapsed_time)

class Timer(object):
    def __init__(self, callback=None):
        """
        Constructs a Timer object
        @param callback: a callable that is called when we are done taking
            the time and that is passed the present timer object
        @type callback: callable
        """
        self.callback = callback
        self._start_time = None
        self._end_time = None

    @property
    def start_time(self):
        """
        The time when the with block started executing.
        """
        if self._start_time is None:
            raise TimerStateError("Not __entered__ yet.")
        return self._start_time

    @property
    def end_time(self):
        """
        The time when the with block exited.
        """
        if self._end_time is None:
            raise TimerStateError("Not yet __exited__.")
        return self._end_time

    def tic(self):
        """
        Starts taking the time.
        """
        self._end_time = None
        self._start_time = time.time()

    def __enter__(self):
        self.tic()

    def toc(self):
        """
        Stops taking the time (and calls the callback if not none)
        """
        self._end_time = time.time()
        if callable(self.callback):
            return self.callback(self)

    def __exit__(self, type_, value, traceback):
        if type_ is None and value is None and traceback is None:
            self.toc()

    @property
    def elapsed_time(self):
        """Return the elapsed time"""
        try:
            return (self.end_time - self.start_time) * 1000
        except AttributeError:
            raise TimerStateError()


def tictoc(callback, func, *args, **kwargs):
    """
    Calls func in a timer passing callable as the result.
    @param callback: the callable to execute after the execution
    @type callback: callable
    @param func: the function to benchmark
    @type func: callable
    @param args: Additional arguments passed to func
    @param kwargs: Additional arguments passed to func
    @return: func return value
    """
    t = Timer(callback)
    t.tic()
    try:
        return func()
    finally:
        t.toc()
