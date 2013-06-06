import sys
import importlib
import cProfile

arguments = sys.argv[:]
this_module = arguments.pop(0)

try:
    module_name = arguments.pop(0)
    simulation_factory_name = arguments.pop(0)
    out_name = arguments.pop(0)
except IndexError:
    print 'Missing arguments'
    exit(-1)

module = importlib.import_module(module_name)
simulation_factory = getattr(module, simulation_factory_name)
sim = simulation_factory()

cProfile.run('sim.run(args=arguments)', out_name)
# sim.run(args=arguments)

