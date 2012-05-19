from pynetsym import node_manager
from pynetsym import simulation
from pynetsym import storage
from pynetsym.generation_models import barabasi_albert

import igraph

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA

class BA(simulation.Simulation):
    command_line_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('-m', '--starting-edges', dict(default=5, type=int)))

    activator = Activator

    graph_type = storage.IGraphWrapper
    graph_options = dict(graph=igraph.Graph(0))

    class configurator(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    for starting_size_multiplier in [1, 10, 100, 1000]:
        sim = BA()
        sim.run(starting_edges=)
    
    
    sim = BA()
    sim.run()
    sim.output_processor(igraph.Graph.write, 'ba_%d_%d_%d.graphml' %
            (sim.network_size, sim.steps, sim.starting_edges))
