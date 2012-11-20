import random

from traits.api import Range, Int
from pynetsym import Node, Activator, Simulation, BasicConfigurator


class Node(Node):
    rewiring_probability = Range(low=0.0, high=1.0)
    lattice_connections = Int
    starting_network_size = Int

    def activate(self):
        for index in self.lattice_cw_neighbors():
            neighbors = self.graph.neighbors(self.id)
            if (random.random() < self.rewiring_probability
                    and index in neighbors):
                random_node = self.graph.random_selector.random_node()
                while random_node in neighbors:
                    random_node = self.graph.random_selector.random_node()
                self.graph.remove_edge(self.id, index)
                self.graph.add_edge(self.id, random_node)
            #self.cooperate()

    def lattice_cw_neighbors(self):
        return range(self.id + 1,
                self.id + self.lattice_connections + 1)

    def initialize(self):
        for index in self.lattice_cw_neighbors():
            self.link_to(index % self.starting_network_size)


class Activator(Activator):
    options = {'starting_network_size'}

    to_choose = Int(0, allow_none=False)

    def nodes_to_activate(self):
        node = self.to_choose % self.starting_network_size
        self.to_choose += 1
        return [node]


class WS(Simulation):
    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('-k', '--lattice-connections', dict(default=2, type=int)),
        ('-p', '--rewiring-probability', dict(default=0.3, type=float)))

    activator_type = Activator

    class configurator_type(BasicConfigurator):
        initialize_nodes = True
        node_type = Node
        node_options = {
                "rewiring_probability",
                "lattice_connections",
                "starting_network_size"}
        #options = {"lattice_connections"}

if __name__ == '__main__':
    sim = WS()
    sim.run()

    with sim.graph.handle as graph:
        print graph.number_of_nodes()
        print graph.number_of_edges()
