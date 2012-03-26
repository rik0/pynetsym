import fractions
import random

from pynetsym import simulation, core
import pynetsym
from pynetsym.node_manager import NodeManager


def distribution(s):
    parts = [fractions.Fraction(part) for part in s.split(':')]
    if sum(parts) != 1:
        raise ValueError('Distribution components sum to one.')
    elif len(parts) != 3:
        raise ValueError('Distribution should have three events.')
    else:
        return tuple(float(f) for f in parts)

class Node(core.Node):
    def __init__(self, identifier, address_book, graph,
                 gamma, probability, strategy=None):
        """
        Create a BPA node.

        If a strategy is specified, probability is ignored and strategy
        is simply selected.

        @param identifier: the node id
        @param identifier: int
        @param address_book: the address book
        @param graph: the graph
        @type graph: backend.GraphWrapper
        @param gamma: the bias to select linkers
        @param probability: the probability distribution of the nodes behavior
        @param strategy: the "forced" starting strategy
        """
        super(Node, self).__init__(identifier, address_book, graph)
        self.gamma = gamma
        self.p = probability
        self.strategy = strategy
        if strategy is None:
            self.strategy = self._select_strategy()

    def _select_strategy(self):
        random_value = random.random()
        if random_value < self.p[0]:
            return Node.linker_strategy
        elif random_value < self.p[0] + self.p[1]:
            return Node.inviter_strategy
        else:
            return Node.passive_strategy

    def activate(self):
        self.strategy(self)

    def passive_strategy(self):
        pass ## exactly what we want

    def inviter_strategy(self):
        ## Create a new node: as the node manager answers with a
        ## created node message, then we can link there.
        self.send(
            NodeManager.name, 'create_node', cls=Node,
            parameters=dict(
                gamma=self.gamma, probability=self.p,
                strategy=Node.passive_strategy))

    def created_node(self, identifier):
        self.send(identifier, 'accept_link', originating_node=self.id)

    def linker_strategy(self):
        while 1:
            node = self.graph.preferential_attachment()
            if node in self.graph.handle:
                pass


class BPA(simulation.Simulation):
    class configurator(pynetsym.node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {'probability', 'gamma'}
        activator_cls = simulation.Simulation.activator
        activator_options = {'edges'}

    simulation_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('--gamma', dict(default=0.01, type=float)),
        ('-p', '--probability', dict(default='1/3:1/3:1/3',
                                     type=distribution)),
        ('-e', '--edges', dict(default=4, type=int)))


if __name__ == "__main__":
    bpa = BPA()
    bpa.run()