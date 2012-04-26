import random

from pynetsym import simulation
from pynetsym import node_manager
from pynetsym import core


class Node(core.Node):
    def __init__(self, identifier, address_book,
                 graph, rewiring_probability,
                 lattice_connections, network_size):
        self.rewiring_probability = rewiring_probability
        self.lattice_connections = lattice_connections
        self.network_size = network_size
        super(Node, self).__init__(identifier, address_book, graph)

    def activate(self):
        for index in self.lattice_cw_neighbors():
            neighbors = self.graph.neighbors(self.id)
            if (random.random() < self.rewiring_probability
                    and index in neighbors):
                random_node = self.graph.random_node()
                while random_node in neighbors:
                    random_node = self.graph.random_node()
                self.graph.remove_edge(self.id, index)
                self.graph.add_edge(self.id, random_node)
            self.cooperate()

    def lattice_cw_neighbors(self):
        return range(self.id + 1,
                self.id + self.lattice_connections + 1)

    def initialize(self):
        for index in self.lattice_cw_neighbors():
            self.link_to(index % self.network_size)


class Activator(simulation.Activator):
    def __init__(self, *arguments, **kw):
        super(Activator, self).__init__(*arguments, **kw)
        self.to_choose = 0

    def nodes_to_activate(self):
        node = self.to_choose
        self.to_choose += 1
        return [node]


class WS(simulation.Simulation):
    command_line_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('-k', '--lattice-connections', dict(default=2, type=int)),
        ('-p', '--rewiring-probability', dict(default=0.3, type=float)))

    activator = Activator

    class configurator(node_manager.SingleNodeConfigurator):
        initialize = True
        node_cls = Node
        node_options = {
                "rewiring_probability",
                "lattice_connections",
                "network_size"}
        activator_options = {"lattice_connections"}

if __name__ == '__main__':
    sim = WS()
    sim.run()
