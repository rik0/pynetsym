from traits.trait_types import Int

from pynetsym import Node, Activator, Simulation, BasicConfigurator


class Node(Node):
    starting_edges = Int

    def activate(self):
        forbidden = set()
        assert not len(forbidden)
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.random_selector.preferential_attachment()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1


class Activator(Activator):
    activator_options = {'starting_edges'}

    def nodes_to_activate(self):
        return self.fresh_nodes

    def nodes_to_create(self):
        return [(Node, dict(starting_edges=self.starting_edges))]


class BA(Simulation):
    default_starting_network_size = 5
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_network_size, type=int)),
        ('-m', '--starting-edges',
            dict(default=default_starting_network_size, type=int)))

    activator_type = Activator

#    graph_type = storage.IGraphWrapper
#    graph_options = dict(graph=igraph.Graph(0))

    class configurator_type(BasicConfigurator):
        node_cls = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
#    sim.output_processor(igraph.Graph.write, 'ba_%d_%d_%d.graphml' %
#            (sim.starting_network_size, sim.steps, sim.starting_edges))
