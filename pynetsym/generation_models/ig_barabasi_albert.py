from pynetsym import core
from pynetsym import node_manager
from pynetsym import simulation
from pynetsym import storage

from pynetsym.generation_models import nx_barabasi_albert

import igraph


class BA(nx_barabasi_albert.BA):
    graph_type = storage.IGraphWrapper
    graph_options = dict(graph=igraph.Graph(0))


if __name__ == '__main__':
    sim = BA()
    sim.run()
#    sim.output_processor(igraph.Graph.write, 'ba_%d_%d_%d.graphml' %
#            (sim.starting_network_size, sim.steps, sim.starting_edges))
