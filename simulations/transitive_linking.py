import random
from pynetsym import generation
from pynetsym import core, rnd
from pynetsym import simulation

class Node(core.Node):
    MAX_TRIALS = 10

    def __init__(self, identifier, address_book, graph, death_probability):
        self.death_probability = death_probability
        self.criterion = rnd.random_node
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
        ('--death-probability', dict(default=0.01, type=float)))

    class configurator(generation.SingleNodeConfigurator):
        node_cls = Node
        node_options = {"death_probability"}
        activator_options = {}




