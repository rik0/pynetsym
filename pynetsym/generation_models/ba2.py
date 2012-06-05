from pynetsym import core
from pynetsym import node_manager
from pynetsym import simulation


class Node(core.Node):
    def __init__(self, identifier, address_book,
                 graph, starting_edges):
        super(Node, self).__init__(identifier, address_book, graph)
        self.starting_edges = starting_edges

    def activate(self):
        forbidden = set()
        assert not len(forbidden)
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

#    graph_type = storage.IGraphWrapper
#    graph_options = dict(graph=igraph.Graph(0))

    class configurator_type(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
#    sim.output_processor(igraph.Graph.write, 'ba_%d_%d_%d.graphml' %
#            (sim.starting_network_size, sim.steps, sim.starting_edges))