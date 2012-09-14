import igraph
from traits.trait_types import Float
import random
from traits.traits import Trait

from pynetsym import Node, Simulation, BasicConfigurator
from pynetsym import storage



def select_preferential_attachment(graph):
    return graph.preferential_attachment_node()

def select_uniform(graph):
    return graph.random_node()

class Node(Node):
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

    MAX_TRIALS = 10

    death_probability = Float
    criterion = Trait('uniform',
                      {'uniform': select_uniform,
                       'preferential_attachment': select_preferential_attachment},)
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
                self.link_to(self.criterion_)
        else:
            self.link_to(self.criterion_)

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


class TL(Simulation):
    graph_type = storage.IGraphWrapper
    graph_options = dict(graph=igraph.Graph(0))

    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const='preferential_attachment',
            default='uniform')))

    class configurator_type(BasicConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}


if __name__ == '__main__':
    sim = TL()
    sim.run()
