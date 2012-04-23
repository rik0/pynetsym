from pynetsym import core, node_manager
from pynetsym import simulation
from pynetsym.generation_models import barabasi_albert

class BA(simulation.Simulation):
    command_line_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('-m', '--starting-edges', dict(default=5, type=int)))

    activator = barabasi_albert.Activator

    class configurator(node_manager.SingleNodeConfigurator):
        node_cls = barabasi_albert.Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()