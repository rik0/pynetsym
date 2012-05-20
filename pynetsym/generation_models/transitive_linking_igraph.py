import igraph
import pynetsym
import random

from pynetsym import core
from pynetsym import node_manager
from pynetsym import simulation
from pynetsym import storage


class Node(core.Node):
    MAX_TRIALS = 10

    def __init__(self, identifier, address_book,
                 graph, death_probability, criterion):
        """
        Constructs a new node
        @param identifier: the node identifier
        @type identifier: int
        @param address_book: the usual address book
        @param graph: the network representation
        @type graph: igraph.Graph
        @param death_probability: the probability that a node dies and is
            substituted with a new one
        @param death_probability: float
        @param criterion: the criterion used to chose nodes in case that
            we do not have two friends that are not acquainted
        @type criterion: callable
        """
        self.death_probability = death_probability
        self.criterion = criterion
        super(Node, self).__init__(identifier, address_book, graph)

    def introduction(self):
        graph = self.graph.handle
        neighbors = graph.neighbors(self.id)
        if len(neighbors) > 1:
            for _ in xrange(Node.MAX_TRIALS):
                node_a, node_b = random.sample(neighbors, 2)
                if not graph.are_connected(node_a, node_b):
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
        return self.id

    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        ## Here it may be more efficient never to remove from the graph
        graph = self.graph.handle
        graph.delete_edges((self.id, i) for i in graph.neighbors(self.id))
        target_node = self.graph.random_node()
        self.link_to(target_node)


class TL(simulation.Simulation):
    graph_type = storage.IGraphWrapper
    graph_options = dict(graph=igraph.Graph(0))

    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=lambda graph: graph.preferential_attachment_node(),
            default=lambda graph: graph.random_node())))

    class configurator_type(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}


if __name__ == '__main__':
    sim = TL()
    sim.run()
