import abc
import argparse
import sys
import networkx

from pynetsym import ioutil, core, generation

class Simulation():
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
    L{generation.Activator}, L{networkx.Graph} and L{generation.Clock}.
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
    """the basic options all simulations share. Do not override."""

    @property
    def activator(self):
        """
        Factory used to create the Activator.
        @rtype: callable(graph, address_book)
        """
        return generation.Activator

    @property
    def graph_type(self):
        """
        Returns the factory used to build the graph.
        @rtype: callable
        """
        return networkx.Graph

    @property
    def clock(self):
        """
        Factory used to create the clock.
        @rtype: callable(int steps, address_book) -> core.Clock
        """
        return generation.Clock

    @abc.abstractproperty
    def simulation_options(self):
        """
        Returns a sequence of tuples:

        Each option line is in the form:
            1. (short_option_name, long_option_name, parameters)
            2. (long_option_name, parameters)

        @rtype: [(str, str, dict)]
        """

    @abc.abstractproperty
    def configurator(self):
        """
        Returns the builder of the Configurator to be passed to NodeManager
        @rtype: callable
        """

    def __init__(self):
        self.graph = self.graph_type()

    def _build_parser(self):
        parser = argparse.ArgumentParser(
            add_help=False,
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


    def run(self, args=None, **kwargs):
        """
        Runs the simulation.
        @param args: an array of command line options which is parsed with
            L{parse_arguments}. Default value=None. If it is None and no
            options have been passed with kwargs, sys.argv[1:] is processed
        @param kwargs: option relevant for the model can be passed as keyword
            options and they override values in args.
        @keyword steps: the number of simulations steps to perform
        @keyword output: the output file to save the network in
        @keyword format: the format to save the network in
        @attention: output and format are presently not working and are vestiges
            of an older version. However, we plan to add support for "easy"
            saving of networks which may make use of them and thus have not
            removed the options right now.
        @return: None

        @warning: The idea here is either to call this method with all keyword
            arguments or with no arguments at all (in the case the program
            is run as a standalone script). However, it also makes sense to
            override (in the standalone script case) individual options.
            Deliberately mixing arguments passed with an array in args and
            keywords arguments (although working) is strongly discouraged.
        """
        if args is None:
            args = [] if kwargs else sys.argv[1:]
        arguments_dictionary = self.parse_arguments(args[1:])
        arguments_dictionary.update(kwargs)
        self.output_path = arguments_dictionary.pop('output')
        self.format = arguments_dictionary.pop('format')
        steps = arguments_dictionary.pop('steps')

        address_book = core.AddressBook()
        node_manager = core.NodeManager(
            self.graph, address_book,
            self.configurator(**arguments_dictionary))
        node_manager.start()

        activator = self.activator(self.graph, address_book)
        activator.start()

        clock = self.clock(steps, address_book)
        clock.start()

        activator.join()

