"""
Barabasi-Albert Model with NetworkX backend.

Barabasi AL, Albert R (1999) Emergence of scaling in random networks. Science 286:509-51
"""

from traits.trait_types import Int
from pynetsym import Node, Activator, Simulation, BasicConfigurator


class Node(Node):
    starting_edges = Int

    def activate(self):
        forbidden = set()
        forbidden.add(self.id)
        rs = self.graph.random_selector
        while self.starting_edges:
            random_node = rs.preferential_attachment()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1


class Activator(Activator):
    options = {'starting_edges'}

    def nodes_to_activate(self):
        # fresh_nodes holds the collection of nodes
        # that have just been created.
        return self.fresh_nodes

    def nodes_to_create(self):
        # create just a node of type Node and passing it
        # the attribute `starting_edge'
        return [(Node, dict(starting_edges=self.starting_edges))]


class BA(Simulation):
    default_starting_network_size = 5
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_network_size, type=int)),
        ('-m', '--starting-edges',
            dict(default=default_starting_network_size, type=int)))

    activator_type = Activator

    class configurator_type(BasicConfigurator):
        node_type = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
