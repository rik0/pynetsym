import copy
import sys
import operator

import gevent
from gevent.greenlet import LinkedCompleted

from traits.api import Int
from traits.api import List
from traits.api import true
from traits.api import false
from traits.api import Instance

from pynetsym import addressing
from pynetsym import graph
from pynetsym import agent_db
from pynetsym import configuration
from pynetsym import core
from pynetsym import termination
from pynetsym import timing

from pynetsym.util import extract_subdictionary
from pynetsym.util import SequenceAsyncResult
from pynetsym.util import gather_from_ancestors
from pynetsym.util import classproperty

from pynetsym.agent_db import PythonPickler
from pynetsym.node_manager import NodeManager
from pynetsym.termination import TerminationChecker
from pynetsym.util.component_creator import ComponentCreator


__all__ = [
    'Simulation',
    'Activator',
    'AsyncClock',
    'Clock'
]

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
    activator_options = {'graph'}

    def __init__(self, graph, **additional_arguments):
        activator_options = gather_from_ancestors(
            self, 'activator_options')
        activator_arguments = extract_subdictionary(
            additional_arguments,
            activator_options)
        self.graph = graph
        vars(self).update(activator_arguments)

    def activate_nodes(self):
        node_ids = self.nodes_to_activate()
        for node_id in node_ids:
            self.send(node_id, 'activate')

    def destroy_nodes(self):
        self.dying_nodes = self.nodes_to_destroy()
        for node_id in self.dying_nodes:
            # notice: this is "beautifully" queued
            self.send(node_id, 'kill')

    def create_nodes(self):
        to_create = self.nodes_to_create()
        node_ids = SequenceAsyncResult(
            [self.send(NodeManager.name, 'create_node',
                       cls=node_class, parameters=node_parameters)
             for node_class, node_parameters in to_create])
        self.fresh_nodes = node_ids.get()

    def simulation_ended(self):
        return self.send(NodeManager.name, 'simulation_ended').get()

    def tick(self):
        self.destroy_nodes()
        self.create_nodes()
        self.activate_nodes()

    def signal_termination(self, reason):
        self.send(TerminationChecker.name, 'require_termination',
                reason=reason).get()

    def nodes_to_activate(self):
        return [self.graph.random_selector.random_node()]

    def nodes_to_destroy(self):
        return {}

    def nodes_to_create(self):
        return {}


class SyncActivator(Activator):
    """
    This Activator variant always waits for the nodes to acknowledge the
    activate message, thus making it essentially serial.
    """

    def activate_nodes(self):
        node_ids = self.nodes_to_activate()
        for node_id in node_ids:
            done = self.send(node_id, 'activate')
            done.get()


class BaseClock(core.Agent):
    name = 'clock'
    activator_can_terminate = false()
    clock_loop_g = Instance(gevent.Greenlet)

    active = true(transient=True)
    observers = List

    def register_observer(self, name):
        self.observers.append(name)

    def unregister_observer(self, name):
        self.observers.remove(name)

    def join(self):
        try:
            return super(BaseClock, self).join()
        except LinkedCompleted:
            return True

    def start_clock(self):
        """
        Here the clock actually starts ticking.
        """
        self.active = True
        self.clock_loop_g = gevent.spawn_link(self.clock_loop)

    def positive_termination(self, originator, motive):
        if originator == TerminationChecker.name:
            self.clock_loop_g.join()

    def clock_loop(self):
        raise NotImplementedError()

    def send_tick(self):
        for observer in self.observers:
            self.send(observer, 'ticked')
        return self.send(Activator.name, 'tick')

    def send_simulation_ended(self):
        return self.send(Activator.name, 'simulation_ended')

    def simulation_end(self):
        self.active = False
        self.send_simulation_ended().get()

    def ask_to_terminate(self):
        return self.send(
            termination.TerminationChecker.name, 'check',
            requester=self.name)


class AsyncClock(BaseClock):
    remaining_ticks = Int

    def clock_loop(self):
        while self.remaining_ticks:
            self.send_tick()
            self.remaining_ticks -= 1
        else:
            self.simulation_end()


class Clock(BaseClock):
    def clock_loop(self):
        while self.active:
            waiting = self.send_tick()
            waiting.get()
            should_terminate = self.ask_to_terminate()
            self.active = not should_terminate.get()
        else:
            self.simulation_end()

class Simulation(object):
    """
    A subclass of Simulation describes a specific kind of simulation.

    Some parameters have to be overridden to customize behavior. Most of
    these parameters may be class parameters in the overridden class as well
    as instance variables. It is for example acceptable to define an
    enclosed class `activator_type` that "satisfies" the need for an L{activator_type}
    attribute.
        1. L{Simulation.activator_type}: the callable that creates the activator_type
            for the simulation
        2. L{Simulation.graph_type}: the callable that creates the graph
            which holds the network.
        3. L{Simulation.clock_type}: the callable that creates the clock_type in the
            simulation
        4. L{Simulation.command_line_options}
        5. L{Simulation.configurator_type}

    Of these, L{Simulation.activator_type}, L{Simulation.graph_type},
    L{Simulation.command_line_options} and
    L{Simulation.clock_type} have sensible default values (respectively,
    L{generation.Activator}, L{backend.NXGraphWrapper},
    a list of default options and L{generation.Clock}.
    The other arguments need to be supplied by the subclass.

    Notice that command_line_options are scanned along the inheritance
    tree and put all together in a single list before being processed.
    As a consequence it is an error to choose options with names already
    used in superclasses. As the Simulation class hierarchies are meant
    to be small, this should not be a problem and greatly simplify the
    design.

    The preferred way to deal with these options is like::
        class SimulationSubclass(Simulation):
            class activator_type(Activator):
                # ...

            class configurator_type(generation.BasicConfigurator):
                node_cls = Node
                node_options = {...}
                activator_options = {...}

            command_line_options = (
                ('-b', '--bar', dict(default=..., type=...))
    """

    command_line_options = (
        ("-s", "--steps", dict(default=100, type=int)),
        )
    """
    Each option line is in the form:
        1. (short_option_name, long_option_name, parameters)
        2. (long_option_name, parameters)
    """

    additional_agents = ()

    @classproperty
    def activator_type(self):
        """
        Factory used to create the Activator.
        @rtype: callable(graph, address_book)
        """
        return Activator

    @classproperty
    def graph_type(self):
        """
        Returns the factory used to build the graph.
        @rtype: callable
        """
        return graph.default_graph

    @classproperty
    def clock_type(self):
        """
        Factory used to create the clock_type.
        @rtype: callable(int steps, address_book) -> core.Clock
        """
        return Clock


    @classproperty
    def termination_checker_type(self):
        return TerminationChecker

    @property
    def termination_checker_options(self):
        return [termination.count_down(self.steps)]

    @classproperty
    def configurator_type(self):
        """
        Returns the builder of the Configurator to be passed to NodeManager
        @rtype: callable
        """

    def __init__(self):
        """
        During the initialization step we create a new graph according to
        the property graph_type. Additional parameters can be passed to
        graph_type setting the attribute graph_options to a dictionary.
        @return:
        """
        object.__setattr__(self, '_simulation_parameters', {})
        self._set_parameters = False
        self.graph = None
        # do not register the node_add because that is done when
        # the id is extracted from id_manager
        self.callback = timing.TimeLogger(sys.stdout)
        self.address_book = None


    def add_parameter(self, key, value):
        self._simulation_parameters[key] = value

    def remove_parameter(self, key):
        self._simulation_parameters.pop(key)

    def update_parameters(self, cli_args_dict):
        self._simulation_parameters.update(cli_args_dict)

    def __getattr__(self, name):
        try:
            return self._simulation_parameters[name]
        except KeyError, e:
            raise AttributeError(e.message)

    def __setattr__(self, name, value):
        if name in self._simulation_parameters:
            raise AttributeError('Read only attribute %s.' % name)
        else:
            object.__setattr__(self, name, value)

    def setup_parameters(self, args=None, force_cli=False, **kwargs):
        cli_args_dict = self.build_parameters(args, force_cli, kwargs)
        self._set_parameters = True
        self.update_parameters(cli_args_dict)

    def get_parameters(self):
        return self._simulation_parameters.copy()

    @classmethod
    def build_parameters(cls, args, force_cli, kwargs):
        options = gather_from_ancestors(
            cls, 'command_line_options', list)
        configuration_manager = configuration.ConfigurationManager(options)
        if (args is None and not kwargs) or force_cli:
            configuration_manager.consider_command_line()
        configuration_manager.consider(args)
        configuration_manager.consider(kwargs)
        cli_args_dict = configuration_manager.process()
        return cli_args_dict

    @classmethod
    def gather_additional_agents(cls):
        return gather_from_ancestors(
            cls, 'additional_agents', acc_type=set)

    def setup(self):
        graph_creator = ComponentCreator(self, 'graph')
        graph_creator.build(set_=True)

    def create_node_db(self):
        self.node_db = agent_db.AgentDB(PythonPickler(), dict())


    def create_address_book(self):
        node_address_book = addressing.FlatAddressBook()
        main_address_book = addressing.FlatAddressBook()
        self.address_book = addressing.AutoResolvingAddressBook(
            main=main_address_book, node=node_address_book)
        self.address_book.add_resolver('node', operator.isNumberType)
        self.address_book.add_resolver('main',
                                       lambda o: isinstance(o, basestring))

    def create_logger(self):
        self.logger = core.get_logger(
            self.address_book, self.node_db, sys.stderr)

    def create_service_agents(self):
        self.create_node_db()
        self.create_address_book()
        self.create_logger()
        termination_checker_options = gather_from_ancestors(self,
            'termination_checker_options', list)
        self.termination_checker = self.termination_checker_type(
                self.graph,
                *termination_checker_options)
        self.configurator = self.configurator_type(
            **self._simulation_parameters)
        self.node_manager = NodeManager(self.graph)

    def pre_configure_network(self):
        self.configurator.start(self.address_book, self.node_db)
        # FIXME: clean this code! Too much dependence from internals!
        self.node_manager._greenlet.link(self.configurator._greeenlet)
        self.configurator.join()
        self.node_manager._greenlet.unlink(self.configurator._greeenlet)


    def create_simulation_agents(self):
        self.termination_checker.start(self.address_book, self.node_db)
        self.node_manager.start(self.address_book, self.node_db)
        self.activator = self.activator_type(
            self.graph,
            **self._simulation_parameters)
        self.activator.start(self.address_book, self.node_db)
        self.clock = self.clock_type(
            **getattr(self, 'clock_options', {}))
        self.clock.start(self.address_book, self.node_db)
        additional_agents = self.gather_additional_agents()
        for (additional_agent_factory, args, kwargs) in additional_agents:
            additional_agent = additional_agent_factory(*args, **kwargs)
            additional_agent.start(self.address_book, self.node_db)

    def start_simulation(self):
        self.clock.start_clock()

    def run(self, args=None, force_cli=False, **kwargs):
        """
        Runs the simulation.
        @param args: a string of command line options parsed with
            L{parse_arguments}. Default value=None. If it is None and no
            options have been passed with kwargs, sys.argv[1:] is processed
        @param kwargs: option relevant for the model can be passed as
            keyword options and they override values in args.
        @attention: output and format are presently not working and are
            vestiges of an older version. However, we plan to add support
            for "easy" saving of networks which may make use of them and
            thus have not removed the options right now.
        @return: The current simulation so that it is easier to create
            one-liners
        @rtype: Simulation

        @warning: The idea here is either to call this method with all
            keyword arguments or with no arguments at all (in the case the
            program is run as a standalone script). However, it also makes
            sense to override (in the standalone script case) individual
            options.  Deliberately mixing arguments passed with an array in
            args and keywords arguments (although working) is strongly
            discouraged.
        """
        if not self._set_parameters:
            self.setup_parameters(args, force_cli, **kwargs)
        else:
            self.update_parameters(kwargs)

        self.setup()

        self.create_service_agents()
        self.create_simulation_agents()
        self.pre_configure_network()
        with timing.Timer(self.callback):
            self.start_simulation()
            self.clock.join()
            return self

    def exception_hook(self, node):
        raise node.exception

    def output_processor(self, processor, *additional_arguments):
        self.graph.output_processor(processor, *additional_arguments)

    @property
    def handle(self):
        return self.graph.handle

    @property
    def motive(self):
        return self.termination_checker.motive


