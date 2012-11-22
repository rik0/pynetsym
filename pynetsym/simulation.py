import sys
import operator

import gevent
from gevent.greenlet import LinkedCompleted

from traits.api import Int
from traits.api import List
from traits.api import true
from traits.api import false
from traits.api import Instance

from pynetsym import addressing, Logger
from pynetsym import graph
from pynetsym import agent_db
from pynetsym import configuration
from pynetsym import core
from pynetsym import termination
from pynetsym import timing

from pynetsym.util import SequenceAsyncResult
from pynetsym.util import gather_from_ancestors

from pynetsym.agent_db import PythonPickler
from pynetsym.node_manager import NodeManager
from pynetsym.termination import TerminationChecker
from pynetsym.util.component_builder import ComponentBuilder


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




class AdditionalAgentComponentBuilder(ComponentBuilder):
    def __init__(self, context, additional_agent_line):
        (component_name, gfa, start_after_clock) =\
            self.parse_additional_agent_line(additional_agent_line)
        self.start_after_clock = start_after_clock
        super(AdditionalAgentComponentBuilder, self).__init__(
            context, component_name, gfa)

    def parse_additional_agent_line(self, additional_agent_line):
        try:
            (component_name, gfa,
             start_after_clock) = additional_agent_line
        except TypeError:
            component_name = additional_agent_line
            start_after_clock = False
            gfa = False
        except ValueError:
            if len(additional_agent_line) == 2:
                (component_name, gfa) = additional_agent_line
                start_after_clock = False
            else:
                component_name = additional_agent_line
                start_after_clock = False
                gfa = False
        return component_name, gfa, start_after_clock




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
                node_type = Node
                node_options = {...}
                options = {...}

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

    activator_type = Activator
    graph_type = graph.default_graph
    clock_type = Clock
    logger_type = Logger
    termination_checker_type = TerminationChecker
    configurator_type = None

    @property
    def termination_checker_conditions(self):
        return [termination.count_down(self.steps)]

    @property
    def termination_checker_parameters(self):
        return dict(
            graph=self.graph,
            conditions=self.termination_checker_conditions)

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

    def setup(self):
        graph_builder = ComponentBuilder(self, 'graph')
        graph_builder.build(set_=True)

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
        logger_builder = ComponentBuilder(self, 'logger')
        logger_builder.build(stream=sys.stderr)\
            .start(self.address_book, self.node_db)


    def create_termination_checker(self):
        termination_checker_builder = ComponentBuilder(
            self, 'termination_checker')
        termination_checker_builder.build(set_=True)
        self.termination_checker.start(self.address_book, self.node_db)

    def create_configurator(self):
        configurator_builder = ComponentBuilder(
            self, 'configurator', gather_from_ancestors=True)
        configurator_builder.build(
            self._simulation_parameters,
            set_=True,
            full_parameters=self._simulation_parameters)

    def create_node_manager(self):
        self.node_manager = NodeManager(self.graph)

    def create_service_agents(self):
        self.create_node_db()
        self.create_address_book()
        self.create_logger()
        self.create_termination_checker()
        self.create_configurator()
        self.create_node_manager()

    def link_node_manager_with_configurator(self):
        # FIXME: clean this code! Too much dependence from internals!
        self.node_manager._greenlet.link(self.configurator._greeenlet)
        self.configurator.join()
        self.node_manager._greenlet.unlink(self.configurator._greeenlet)

    def pre_configure_network(self):
        self.node_manager.start(self.address_book, self.node_db)

        self.configurator.start(self.address_book, self.node_db)
        self.link_node_manager_with_configurator()


    def create_activator(self):
        activator_builder = ComponentBuilder(
            self, 'activator', gather_from_ancestors=True)
        activator_builder.build(self._simulation_parameters,
                                set_=True, graph=self.graph)
        self.activator.start(self.address_book, self.node_db)

    def create_clock(self):
        clock_builder = ComponentBuilder(
            self, 'clock')
        clock_builder.build(set_=True)
        self.clock.start(self.address_book, self.node_db)

    def create_additional_agents(self):
        additional_agents = gather_from_ancestors(
                    self, 'additional_agents', acc_type=set)
        self.late_start = []
        for additional_agent_line in additional_agents:
            component_builder = AdditionalAgentComponentBuilder(
                self, additional_agent_line)
            component = component_builder.build(
                parameters=self._simulation_parameters, set_=True)
            if component_builder.start_after_clock:
                self.late_start.append(component)
            else:
                component.start(self.address_book, self.node_db)

    def create_simulation_agents(self):
        self.create_activator()
        self.create_clock()
        self.create_additional_agents()

    def start_simulation(self):
        self.clock.start_clock()
        for component in self.late_start:
            component.start(self.address_book, self.node_db)

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
