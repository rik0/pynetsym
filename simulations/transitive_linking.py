import random
from pynetsym import generation
from pynetsym import core, rnd
from pynetsym import simulation
from pynetsym import choice_criteria

class Node(core.Node):
    MAX_TRIALS = 10

    def __init__(self, identifier, address_book,
                 graph, death_probability, criterion):
        self.death_probability = death_probability
        self.criterion = criterion
        super(Node, self).__init__(identifier, address_book, graph)

    def introduction(self):
        graph = self.graph
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

    def activate(self):
        if random.random() < self.death_probability:
            self.regenerate()
        else:
            self.introduction()

    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        self.graph.remove_node(self.id)
        target_node = rnd.random_node(self.graph)
        self.link_to(target_node)

class TL(simulation.Simulation):
    simulation_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=choice_criteria.preferential_attachment,
            default=rnd.random_node)))

    class configurator(generation.SingleNodeConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}
        activator_options = {}




