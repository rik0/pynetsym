import sys
import copy

from pynetsym import core
from pynetsym import configuration
from pynetsym import timing
from pynetsym import metautil
from pynetsym import geventutil
from pynetsym import termination
from pynetsym import argutils
from pynetsym.node_manager import NodeManager, IdManager
from pynetsym import storage
from pynetsym.storage.basic import NotifyingGraphWrapper


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

            class configurator_type(generation.SingleNodeConfigurator):
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

    @metautil.classproperty
    def activator_type(self):
        """
        Factory used to create the Activator.
        @rtype: callable(graph, address_book)
        """
        return Activator

    @metautil.classproperty
    def graph_type(self):
        """
        Returns the factory used to build the graph.
        @rtype: callable
        """
        return storage.NXGraphWrapper

    @metautil.classproperty
    def clock_type(self):
        """
        Factory used to create the clock_type.
        @rtype: callable(int steps, address_book) -> core.Clock
        """
        return Clock

    @metautil.classproperty
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

        graph_options = getattr(self, 'graph_options', {})
        ## deepcopy: no object sharing between different simulation
        ## executions!
        graph_options = copy.deepcopy(graph_options)
        self.graph = NotifyingGraphWrapper(
            self.graph_type(**graph_options))
        self.id_manager = IdManager()
        self.graph.register_observer(
            self.id_manager.node_removed,
            NotifyingGraphWrapper.REMOVE,
            NotifyingGraphWrapper.NODE)
        # do not register the node_add because that is done when
        # the id is extracted from id_manager
        self.callback = timing.TimeLogger(sys.stdout)

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
        self.update_parameters(cli_args_dict)

    def get_parameters(self):
        return self._simulation_parameters.copy()

    @classmethod
    def build_parameters(cls, args, force_cli, kwargs):
        options = metautil.gather_from_ancestors(
            cls, 'command_line_options', list)
        configuration_manager = configuration.ConfigurationManager(options)
        if (args is None and not kwargs) or force_cli:
            configuration_manager.consider_command_line()
        configuration_manager.consider(args)
        configuration_manager.consider(kwargs)
        cli_args_dict = configuration_manager.process()
        return cli_args_dict

    def set_up(self):
        pass

    def create_service_agents(self):
        self.address_book = core.AddressBook(self.graph)
        self.termination_checker = termination.TerminationChecker(self.graph,
            self.address_book, termination.count_down(self.steps))
        self.configurator_type = self.configurator_type(
            self.address_book, **self._simulation_parameters)
        self.node_manager = NodeManager(
            self.graph, self.address_book,
            self.id_manager)

    def pre_configure_network(self):
        self.termination_checker.start()
        self.node_manager.start()
        self.configurator_type.start()
        self.configurator_type.join()

    def create_simulation_agents(self):
        self.activator = self.activator_type(self.graph, self.address_book,
            **self._simulation_parameters)
        self.activator.start()
        self.clock = self.clock_type(self.address_book)

    def start_simulation(self):
        self.clock.start()

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

        self.set_up()

        self.create_service_agents()
        self.pre_configure_network()
        self.create_simulation_agents()
        with timing.Timer(self.callback):
            self.start_simulation()

            self.termination_checker.join()
            if self.node_manager.failures:
                sys.exit(1)
            return self

    def exception_hook(self, node):
        raise node.exception

    def output_processor(self, processor, *additional_arguments):
        self.graph.output_processor(processor, *additional_arguments)


class Activator(core.Agent):
    """
    The Activator chooses what happens at each step of the simulation.

    The tick method is called at each simulation step. The default behavior
    is to call choose_node to select a random node and send it an activate
    message.

    tick, simulation_ended and choose_node are meant to be overrode by
    implementations.
    """
    name = 'activator_type'
    activator_options = {}

    def __init__(self, graph, address_book, **additional_arguments):
        super(Activator, self).__init__(self.name, address_book)
        activator_options = metautil.gather_from_ancestors(
            self, 'activator_options')
        activator_arguments = argutils.extract_options(
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
        node_ids = geventutil.SequenceAsyncResult(
            [self.send(NodeManager.name, 'create_node',
                       cls=node_class, parameters=node_parameters)
             for node_class, node_parameters in to_create])
        self.fresh_nodes = node_ids.get()

    def tick(self):
        self.destroy_nodes()
        self.create_nodes()
        self.activate_nodes()

    def nodes_to_activate(self):
        return [self.graph.random_node()]

    def nodes_to_destroy(self):
        return {}

    def nodes_to_create(self):
        return {}


class Clock(core.Agent):
    name = 'clock_type'
    activator_can_terminate = False

    def __init__(self, address_book):
        super(Clock, self).__init__(self.name, address_book)
        self.activator_type = address_book.resolve(Activator.name)
        self.active = True

    def send_tick(self):
        return self.send(Activator.name, 'tick')

    def simulation_end(self):
        self.active = False

    def ask_to_terminate(self):
        return self.send(
            termination.TerminationChecker.name, 'check')

    def _run(self):
        while self.active:
            done = self.send_tick()
            if done.get() and self.activator_can_terminate:
                self.simulation_end()
            else:
                should_stop = self.ask_to_terminate().get()
                if should_stop:
                    self.simulation_end()
