import sys
import core, timing
import rnd

__author__ = 'enrico'

# TODO: activator shall activate, destroy & create nodes
# TODO: the functions shall be parameters (choice functions and actions?)
class Activator(core.Agent):
    name = 'activator'
    def __init__(self, graph, address_book):
        super(Activator, self).__init__(self.name, address_book)
        self.graph = graph

    def tick(self):
        node_id = self.choose_node()
        self.send(node_id, 'activate')

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


def generate(
    graph, module, steps,
    timer_callback=None,
    **additional_arguments):
    with timing.Timer(timer_callback):
        address_book = core.AddressBook()
        node_manager = core.NodeManager(graph, address_book,
                                        module.make_setup(**additional_arguments))
        node_manager.start()

        activator = Activator(graph, address_book)
        activator.start()

        clock = Clock(steps, address_book)
        clock.start()

        activator.join()
        #node_manager.join()