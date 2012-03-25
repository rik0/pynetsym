from pynetsym import simulation

import unittest

class DummySimulationShort(simulation.Simulation):
    command_line_options = (
      ('-o', '--orcs', dict()),)

class DummySimulationLong(simulation.Simulation):
    command_line_options = (
      ('--output',  dict()),)

class DuplicatedOptions(unittest.TestCase):
    def testShortDuplicated(self):
        self.assertRaises(
                simulation.ConfigurationError,
                DummySimulationShort().run)
    def testLongDuplicated(self):
        self.assertRaises(
                simulation.ConfigurationError,
                DummySimulationLong().run)
