import core
import rnd

__author__ = 'enrico'

# TODO: activator shall activate, destroy & create nodes
# TODO: the functions shall be parameters (choice functions and actions?)
class Activator(core.Agent):
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
        return rnd.random_node(self.graph)

class Clock(core.Agent):
    name = 'clock'
    def __init__(self, max_steps, address_book):
        super(Clock, self).__init__(self.name, address_book)
        self.max_steps = max_steps
        self.activator = address_book.resolve(Activator.name)

    def _run(self):
        for step in xrange(self.max_steps):
            self.send(Activator.name, 'tick')
        self.send(Activator.name, 'simulation_ended')


def make_activator(max_steps, activate_function, graph, address_book):
    activator = Activator(activate_function, graph, address_book)
    clock = Clock(max_steps, address_book)
    activator.start()
    #gevent.sleep(0)
    clock.start()
    return activator