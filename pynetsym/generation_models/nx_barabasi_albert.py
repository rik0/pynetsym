from pynetsym import node_manager
from pynetsym import simulation
from pynetsym.generation_models import barabasi_albert


class BA(simulation.Simulation):
    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('-m', '--starting-edges', dict(default=5, type=int)))

    activator_type = barabasi_albert.Activator

    class configurator_type(node_manager.SingleNodeConfigurator):
        node_cls = barabasi_albert.Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
