import random
from pynetsym import core, node_manager
from pynetsym import simulation

class Node(core.Node):
    MAX_TRIALS = 10

    def __init__(self, identifier, address_book,
                 graph, death_probability, criterion):
        self.death_probability = death_probability
        self.criterion = criterion
        super(Node, self).__init__(identifier, address_book, graph)

    def introduction(self):
        graph = self.graph.handle
        neighbors = graph.neighbors(self.id)
        if len(neighbors) > 1:
            for _ in xrange(Node.MAX_TRIALS):
                node_a, node_b = random.sample(neighbors, 2)
                if not graph.has_edge(node_a, node_b):
                    self.send(node_a, 'introduce_to', target_node=node_b)
                    break
            else:
                self.link_to(self.criterion)
        else:
            self.link_to(self.criterion)

    @core.answers('activation_received', node_id='id')
    def activate(self):
        if random.random() < self.death_probability:
            self.regenerate()
        else:
            self.introduction()

    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        self.graph.switch_node(self.id, self)
        target_node = self.graph.random_node()
        self.link_to(target_node)

class TL(simulation.Simulation):
    command_line_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=lambda graph: graph.preferential_attachment_node(),
            default=lambda graph: graph.random_node())))

    class configurator(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}

if __name__ == '__main__':
    sim = TL()
    sim.run()
