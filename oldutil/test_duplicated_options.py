from oldutil import metautil
from pynetsym import configuration
from pynetsym import simulation

import py
import unittest


class DummySimulationShort(simulation.Simulation):
    command_line_options = (
      ('-s', '--super', dict()),)


class DummySimulationLong(simulation.Simulation):
    command_line_options = (
      ('--steps',  dict()),)

@py.test.mark.parametrize(("cls", ), [
    (DummySimulationShort, ),
    (DummySimulationLong, ),
])
def test_duplicated_options(cls):
    empty_arguments = []
    options = metautil.gather_from_ancestors(cls, 'command_line_options', list)

    py.test.raises(configuration.ConfigurationError,
        configuration.ConfigurationManager, options)
