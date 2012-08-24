from pynetsym import core
from pynetsym import node_manager
from pynetsym import simulation
from pynetsym.nodes import Node


class Node(Node):
    def __init__(self, identifier, address_book,
                 graph, starting_edges):
        super(Node, self).__init__(identifier, address_book, graph)
        self.starting_edges = starting_edges

    def activate(self):
        forbidden = set()
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.preferential_attachment_node()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1


class Activator(simulation.Activator):
    activator_options = {'starting_edges'}

    def nodes_to_activate(self):
        return self.fresh_nodes

    def nodes_to_create(self):
        return [(Node, dict(starting_edges=self.starting_edges))]


class BA(simulation.Simulation):
    default_starting_network_size = 5
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_network_size, type=int)),
        ('-m', '--starting-edges',
            dict(default=default_starting_network_size, type=int)))

    activator_type = Activator

    class configurator_type(node_manager.BasicConfigurator):
        node_cls = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
