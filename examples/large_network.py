import networkx as nx

from pynetsym import core, configurators, simulation


class Node(core.Node):
    def activate(self):
        pass

class Simulation(simulation.Simulation):
    class configurator_type(configurators.StartingNXGraphConfigurator):
        node_cls = Node
        node_options = {}
        
        
g = nx.powerlaw_cluster_graph(100000, 20, 0.1)


sim = Simulation()
sim.run(starting_graph=g)