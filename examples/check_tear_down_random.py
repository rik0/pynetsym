import random
import networkx as nx

from pynetsym import core, BasicConfigurator
from pynetsym import simulation
from pynetsym import node_manager
from pynetsym.nodes import Node

class Node(Node):
    #DEBUG_SEND = True
    #DEBUG_RECEIVE = True

    def __init__(self, identifier, address_book, graph, starting_network_size):
        super(Node, self).__init__(identifier, address_book, graph)
        self.starting_network_size = starting_network_size
        self.all_nodes = range(self.starting_network_size)

    def activate(self):
        nodes = random.sample(
            self.all_nodes,
            random.randrange(0, self.starting_network_size)
        )
        for node in nodes:
            self.link_to(node)

class Activator(simulation.Activator):
    #DEBUG_SEND = True
    #DEBUG_RECEIVE = True

    options = {'starting_network_size'}

    def setup(self):
        self.next_node = 0

    def nodes_to_activate(self):
        node = random.choice(range(self.starting_network_size))
        return [node]


class Sim(simulation.Simulation):
    default_starting_nodes = 20
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_nodes, type=int)),
    )

    activator_type = Activator

    class configurator_type(BasicConfigurator):
        node_type = Node
        node_options = {'starting_network_size'}


if __name__ == '__main__':
    sim = Sim()
    graph = sim.graph.handle
    assert isinstance(graph, nx.Graph)

    sim.run()

