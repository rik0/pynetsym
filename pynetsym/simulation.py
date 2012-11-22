import copy
import sys
import operator

from pynetsym import addressing
from pynetsym import graph
from pynetsym import agent_db
from pynetsym import configuration
from pynetsym import core
from pynetsym import termination
from pynetsym import timing

from pynetsym.activator import Activator
from pynetsym.clock import Clock

from pynetsym.util import gather_from_ancestors
from pynetsym.util import classproperty

from pynetsym.agent_db import PythonPickler
from pynetsym.node_manager import NodeManager
from pynetsym.termination import TerminationChecker



__all__ = [
    'Simulation',
]


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

    simulation_options = {"steps", "output", "format"}
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
        self._simulation_parameters.get(key)

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
        graph_options = getattr(self, 'graph_options', {})
        ## deepcopy: no object sharing between different simulation
        ## executions!
        graph_options = copy.deepcopy(graph_options)
        self.graph = self.graph_type(**graph_options)


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

    @property
    def handle(self):
        return self.graph.handle

    @property
    def motive(self):
        return self.termination_checker.motive


