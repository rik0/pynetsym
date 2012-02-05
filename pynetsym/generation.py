import abc
import sys
import core, timing
import rnd
import itertools as it
import util

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


class Configurator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **additional_arguments):
        self.activator_arguments = util.subdict(
            additional_arguments, self.activator_options)

    @abc.abstractproperty
    def activator_options(self):
        pass

    @abc.abstractmethod
    def setup(self, node_manager):
        pass


class SingleNodeConfigurator(Configurator):
    def __init__(self, network_size, **additional_arguments):
        self.network_size = network_size
        self.node_arguments, additional_arguments = util.splitdict(
            additional_arguments, self.node_options )
        super(SingleNodeConfigurator, self).__init__(**additional_arguments)

    @abc.abstractproperty
    def identifiers_seed(self):
        pass

    @abc.abstractproperty
    def node_cls(self):
        pass

    @abc.abstractproperty
    def node_options(self):
        pass

    def setup(self, node_manager):
        for identifier in it.islice(
            self.identifiers_seed, 0, self.network_size):
            node_manager.create_node(
                self.node_cls, identifier, self.node_arguments)


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
            module.Configurator(**additional_args))
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