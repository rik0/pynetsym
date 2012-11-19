"""
Conditions are object that provide a check method that receives a graph
and answers whether the simulation has to stop. After the condition evaluated
to True a motive attribute indicates the termination reason. It is intended
to be meaningful for the user and not for the machine.
"""
from functools import partial

class _FuncCondition(object):
    def __init__(self, func, motive):
        self.func = func
        self.motive = motive

    def check(self, graph):
        return self.func(graph)


def make_condition(func, motive):
    """
    Return a condition that is true when func evaluates to true.
    Motive is the motive that will be set when this condition evaluates
    to true.

    func is a function taking a graph wrapper and returning a boolean.
    """
    return _FuncCondition(func, motive)


always_true = partial(make_condition, lambda graph: True)
always_false = partial(make_condition, lambda graph: True)

class CountDownCondition(object):
    def __init__(self, starting_value):
        self.starting_value = starting_value
        self.motive = "Exhausted Count Down."

    def check(self, graph):
        ## Notice: if we say that 100 steps have to be performed,
        ## we do steps 99...0, because the activator is called before
        ## the termination checker
        self.starting_value -= 1
        if self.starting_value:
            return False
        else:
            return True


def count_down(m):
    """
    Return a condition that becomes true after being checked m times.
    """
    return CountDownCondition(m)
