import random
from pynetsym.core import Agent

__author__ = 'enrico'

class Activator(Agent):
    name = 'activator'
    def __init__(self, activate_function, graph, address_book):
        super(Activator, self).__init__(self.name, address_book)
        self.graph = graph
        self.activate_function = activate_function

    def tick(self):
        node_id = self.choose_node()
        self.send(node_id, self.activate_function)

    def simulation_ended(self):
        self.kill()

    def choose_node(self):
        return random.choice(self.graph.nodes())


class Clock(Agent):
    name = 'clock'
    def __init__(self, max_steps, address_book):
        super(Clock, self).__init__(self.name, address_book)
        self.max_steps = max_steps
        self.activator = address_book.resolve(Activator.name)

    def _run(self):
        activator_tick = type(self.activator).tick
        activator_end = type(self.activator).simulation_ended
        for step in xrange(self.max_steps):
            self.send(Activator.name, activator_tick)
        self.send(Activator.name, activator_end)


def make_activator(max_steps, activate_function, graph, address_book):
    activator = Activator(activate_function, graph, address_book)
    clock = Clock(max_steps, address_book)
    activator.start()
    #gevent.sleep(0)
    clock.start()
    return activator