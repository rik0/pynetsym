import networkx as nx
from matplotlib import pyplot as plt

from pynetsym import core
from pynetsym import simulation
from pynetsym import node_manager

class Node(core.Node):
    def __init__(self, identifier, address_book, graph):
        super(Node, self).__init__(identifier, address_book, graph)

    def activate(self):
        for node, _attrs in self.graph.nodes():
            if node != self.id:
                self.link_to(node)


class Activator(simulation.Activator):
    activator_options = {'starting_network_size'}

    def setup(self):
        self.next_node = 0

    def nodes_to_activate(self):
        node = self.next_node
        self.next_node += 1
        if node < self.starting_network_size:
            return [node]
        else:
            return []


class Sim(simulation.Simulation):
    default_starting_nodes = 20
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_nodes, type=int)),
    )

    activator_type = Activator

    class configurator_type(node_manager.BasicConfigurator):
        node_cls = Node


if __name__ == '__main__':
    sim = Sim()
    graph = sim.graph.handle
    assert isinstance(graph, nx.Graph)

    #nx.draw(graph)
    #plt.show()

    sim.run()

    print nx.is_isomorphic(
        nx.complete_graph(len(graph)),
        graph)

    #nx.draw(graph)
    #plt.show()
