import abc
import sys
import core, timing
import rnd
import itertools as it

__author__ = 'enrico'

# TODO: activator shall activate, destroy & create nodes
# TODO: the functions shall be parameters (choice functions and actions?)
class Activator(core.Agent):
    """
    The Activator chooses what happens at each step of the simulation.

    The tick method is called at each simulation step. The default behavior
    is to call choose_node to select a random node and send it an activate
    message.

    tick, simulation_ended and choose_node are meant to be overrode by
    implementations.
    """
    name = 'activator'

    def __init__(self, graph, address_book, **additional_parameters):
        super(Activator, self).__init__(self.name, address_book)
        self.graph = graph
        locals().update(additional_parameters)

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


class Setup(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def activator_options(self):
        pass

    @abc.abstractmethod
    def setup(self, node_manager):
        pass


class SingleNodeSetup(Setup):
    def __init__(self, network_size):
        self.network_size = network_size

    @abc.abstractproperty
    def identifiers_seed(self):
        pass

    @abc.abstractproperty
    def node_cls(self):
        pass

    def setup(self, node_manager):
        generation_seed = it.izip(
            it.repeat(self.node_cls),
            it.islice(self.identifiers_seed, 0, self.network_size),
            it.repeat(self.node_properties))
        for cls, identifier, node_params in generation_seed:
            node_manager.create_node(cls, identifier, node_params)


def generate(graph, module, steps, timer_callback=None, **additional_args):
    """
    Starts the actual simulation
    :param graph: is a NetworkX compatible graph (better if one of pynetsym.graph)
    :param module: a simulation module. In fact it needs to have a make_setup
        method that returns a function taking a NodeManager as argument and
        commanding it how to setup the simulation. Optionally it may have
        an Activator callable attribute that returns an instance of an
        Activator that actually carries on the simulation
    :param steps: the number of steps to perform
    :param timer_callback: a function passed as sole argument to a
        pynetsym.timing.Timer
    :param additional_args: these are forwarded to module.make_setup
    :return: None
    """
    with timing.Timer(timer_callback):
        address_book = core.AddressBook()
        node_manager = core.NodeManager(
            graph, address_book,
            module.make_setup(**additional_args))
        node_manager.start()

        try:
            activator_factory = module.Activator
        except AttributeError:
            activator_factory = Activator

        activator = activator_factory(graph, address_book)
        activator.start()

        clock = Clock(steps, address_book)
        clock.start()

        activator.join()
        #node_manager.join()