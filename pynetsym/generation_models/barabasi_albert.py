from pynetsym import core, node_manager
from pynetsym import simulation

class Node(core.Node):
    def __init__(self, identifier, address_book,
                 graph, starting_edges):
        super(Node, self).__init__(identifier, address_book, graph)
        self.starting_edges = starting_edges

    @core.answers('activation_received', node_id='id')
    def activate(self):
        forbidden = set(self.graph.neighbors(self.id))
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.preferential_attachment_node()
            if (random_node not in forbidden):
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1

class Activator(simulation.Activator):
    activator_options = {'starting_edges'}

    def tick(self):
        self.activations_pending += 1
        self.send(
            node_manager.NodeManager.name,
            'create_node', cls=Node,
            parameters=dict(
                starting_edges=self.starting_edges))

    def created_node(self, identifier):
        self.send(identifier, 'activate')

class BA(simulation.Simulation):
    command_line_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('-m', '--starting-edges', dict(default=5, type=int)))

    activator = Activator

    class configurator(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {'starting_edges'}

if __name__ == '__main__':
    sim = BA()
    sim.run()
