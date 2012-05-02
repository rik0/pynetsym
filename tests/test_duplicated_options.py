from pynetsym import simulation

import unittest


class DummySimulationShort(simulation.Simulation):
    command_line_options = (
      ('-o', '--orcs', dict()),)


class DummySimulationLong(simulation.Simulation):
    command_line_options = (
      ('--output',  dict()),)


class DuplicatedOptions(unittest.TestCase):
    def setUp(self):
        self.empty_arguments = []

    def testShortDuplicated(self):
        self.assertRaises(
                simulation.ConfigurationError,
                DummySimulationShort().run, args=self.empty_arguments)

    def testLongDuplicated(self):
        self.assertRaises(
                simulation.ConfigurationError,
                DummySimulationLong().run, args=self.empty_arguments)
