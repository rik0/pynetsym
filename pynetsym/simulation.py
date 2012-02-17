import abc
import argparse
import sys
import networkx

from pynetsym import ioutil, core, generation

class Simulation():
    basic_options = (
        ("-s", "--steps", dict(default=100, type=int)),
        ("-o", "--output", dict(default=None)),
        ("-f", "--format", dict(choices=ioutil.FORMATS, default=None)))
    """the basic options all simulations share. Do not override."""

    @property
    def activator(self):
        """
        Factory used to create the Activator.

        The preferred method to deal with this in the subclasses is just:

        ::
            class SimulationSubclass(simulation.Simulation):
                class activator(generation.Activator):
                    # ...

        @rtype: generation.Activator
        """
        return generation.Activator

    @property
    def graph_type(self):
        """Returns the factory used to build the graph."""
        return networkx.Graph

    @property
    def clock(self):
        """
        Factory used to create the clock.

        The preferred method to deal with this in the subclasses is just:

        ::
            class SimulationSubclass(simulation.Simulation):
                class clock(generation.Clock):
                    # ...

        @rtype: generation.Clock
        """
        return generation.Clock


    def __init__(self):
        self.graph = self.Graph()

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

        The preferred way to use it in the subclasses is just:

        ::
            class SimulationSubclass(simulation.Simulation):
                class configurator(generation.Configurator):
                    # ...

        @rtype: generation.Configurator
        """

    def _build_parser(self):
        parser = argparse.ArgumentParser(
            add_help=False,
            description='Synthetic Network Generation Utility')
        self._load_arguments(parser, self.basic_options)
        self._load_arguments(parser, self.simulation_options)
        return parser

    def parse_arguments(self, args):
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


    def run(self, args=sys.argv):
        arguments_dictionary = self.parse_arguments(args)
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

