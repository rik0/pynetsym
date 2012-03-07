import argparse
import sys

from pynetsym import ioutil, core, timing, backend, metautil
from pynetsym.node_manager import NodeManager

class Simulation(object):
    """
    A subclass of Simulation describes a specific kind of simulation.

    Some parameters have to be overridden to customize behavior. Most of
    these parameters may be class parameters in the overridden class as well
    as instance variables. It is for example acceptable to define an
    enclosed class `activator` that "satisfies" the need for an L{activator}
    attribute.
        1. L{Simulation.activator}: the callable that creates the activator
            for the simulation
        2. L{Simulation.graph_type}: the callable that creates the graph
            which holds the network.
        3. L{Simulation.clock}: the callable that creates the clock in the
            simulation
        4. L{Simulation.simulation_options}
        5. L{Simulation.configurator}

    Of these, L{Simulation.activator}, L{Simulation.graph_type} and
    L{Simulation.clock} have sensible default values (respectively,
    L{generation.Activator}, L{backend.NXGraph} and L{generation.Clock}.
    The other arguments need to be supplied by the subclass.

    The preferred way to deal with these options is like::
        class SimulationSubclass(Simulation):
            class activator(Activator):
                # ...

            class configurator(generation.SingleNodeConfigurator):
                node_cls = Node
                node_options = {...}
                activator_options = {...}

            simulation_options = (
                ('-b', '--bar', dict(default=..., type=...))

    """
    basic_options = (
        ("-s", "--steps", dict(default=100, type=int)),
        ("-o", "--output", dict(default=None)),
        ("-f", "--format", dict(choices=ioutil.FORMATS, default=None)))
    """the basic options all generation_models share. Do not override."""

    @metautil.classproperty
    def activator(self):
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
        return backend.NXGraph

    @metautil.classproperty
    def clock(self):
        """
        Factory used to create the clock.
        @rtype: callable(int steps, address_book) -> core.Clock
        """
        return Clock

    @metautil.classproperty
    def simulation_options(self):
        """
        Returns a sequence of tuples:

        Each option line is in the form:
            1. (short_option_name, long_option_name, parameters)
            2. (long_option_name, parameters)

        @rtype: [(str, str, dict)]
        """
        return []

    #TODO: fixme
    @metautil.classproperty
    def configurator(self):
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
        graph_options = getattr(self, 'graph_options', {})
        self.graph = self.graph_type(**graph_options)

    def _build_parser(self):
        parser = argparse.ArgumentParser(
            add_help=True,
            description='Synthetic Network Generation Utility')
        self._load_arguments(parser, self.basic_options)
        self._load_arguments(parser, self.simulation_options)
        return parser

    def parse_arguments(self, args):
        """
        Parses an array of command line options into a dictionary
        @param args: the command line options to parse
        @type args: [str]
        @return: a dictionary of options
        @rtype: {str:any}
        """
        parser = self._build_parser()
        namespace = parser.parse_args(args)
        arguments_dictionary = vars(namespace)
        return arguments_dictionary

    def _load_line(self, option_element, parser):
        try:
            short_option, long_option, params = option_element
            parser.add_argument(short_option, long_option, **params)
        except ValueError:
            try:
                long_option, params = option_element
                parser.add_argument(long_option, **params)
            except ValueError:
                parser.add_argument(option_element[0])

    def _load_arguments(self, parser, options):
        """
        Loads options sequence into parser.

        Each option line is in the form:
            1. (short_option_name, long_option_name, parameters)
            2. (long_option_name, parameters)

        @param parser: the parser to configure
        @type parser: argparse.ArgumentParser
        @param options: sequence of options
        """
        for option_element in options:
            self._load_line(option_element, parser)


    def run(self, callback=timing.TimeLogger(sys.stdout),
            *args, **kwargs):
        """
        Runs the simulation.
        @param args: an array of command line options which is parsed with
            L{parse_arguments}. Default value=None. If it is None and no
            options have been passed with kwargs, sys.argv[1:] is processed
        @param kwargs: option relevant for the model can be passed as keyword
            options and they override values in args.
        @keyword steps: the number of generation_models steps to perform
        @keyword output: the output file to save the network in
        @keyword format: the format to save the network in
        @attention: output and format are presently not working and are vestiges
            of an older version. However, we plan to add support for "easy"
            saving of networks which may make use of them and thus have not
            removed the options right now.
        @return: The current simulation so that it is easier to create
            one-liners
        @rtype: Simulation

        @warning: The idea here is either to call this method with all keyword
            arguments or with no arguments at all (in the case the program
            is run as a standalone script). However, it also makes sense to
            override (in the standalone script case) individual options.
            Deliberately mixing arguments passed with an array in args and
            keywords arguments (although working) is strongly discouraged.
        """
        if not args:
            args = [] if kwargs else sys.argv[1:]
        arguments_dictionary = self.parse_arguments(args)
        arguments_dictionary.update(kwargs)
        self.output_path = arguments_dictionary.pop('output')
        self.format = arguments_dictionary.pop('format')
        steps = arguments_dictionary.pop('steps')

        address_book = core.AddressBook()
        node_manager = NodeManager(
            self.graph, address_book,
            self.configurator(**arguments_dictionary))
        node_manager.start()

        activator = self.activator(self.graph, address_book)
        activator.start()

        with timing.Timer(callback):
            clock = self.clock(steps, address_book)
            clock.start()

            activator.join()
            return self

    @classmethod
    def main(cls):
        sim = cls()
        return sim.run()


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
        return self.graph.random_node()


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



