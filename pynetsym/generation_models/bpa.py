"""
Biased preferential attachment.

Kumar R, Novak J, Tomkins A (2010) Structure and evolution of online social networks. In: Yu PSS,
Han J, Faloutsos C (eds) Link mining: models, algorithms, and applications. Springer, New York,
pp 337-357
"""

import fractions
import random
from traits.trait_types import Float, Tuple, Method

from pynetsym import Node, Simulation, BasicConfigurator, NodeManager


def distribution(s):
    parts = [fractions.Fraction(part) for part in s.split(':')]
    if sum(parts) != 1:
        raise ValueError('Distribution components sum to one.')
    elif len(parts) != 3:
        raise ValueError('Distribution should have three events.')
    else:
        return tuple(float(f) for f in parts)


class Node(Node):
    """
    A BPA node.

    If a strategy is specified, probability is ignored and strategy
    is simply selected.

    :param identifier: the node id
    :param identifier: int
    :param address_book: the address book
    :param graph: the graph
    :param gamma: the bias to select linkers
    :param probability: the probability distribution of the nodes
        behavior
    :param strategy: the "forced" starting strategy
    """

    gamma = Float
    probability = Tuple(Float, Float, Float)
    strategy = Method

    def can_be_collected(self):
        return False

    def _strategy_default(self):
        random_value = random.random()
        if random_value < self.probability[0]:
            return self.linker_strategy
        elif random_value < self.probability[0] + self.probability[1]:
            return self.inviter_strategy
        else:
            return self.passive_strategy

    def activate(self):
        self.strategy()
        return self.id

    def passive_strategy(self):
        pass  # exactly what we want

    def inviter_strategy(self):
        ## Create a new node: as the node manager answers with a
        ## created node message, then we can link there.
        self.send(
            NodeManager.name, 'create_node', cls=Node,
            parameters=dict(
                gamma=self.gamma, probability=self.probability,
                strategy=self.passive_strategy))

    def created_node(self, identifier):
        self.send(identifier, 'accept_link', originating_node=self.id)

    def linker_strategy(self):
        pass


class BPA(Simulation):
    class configurator_type(BasicConfigurator):
        node_type = Node
        node_options = {'probability', 'gamma'}

    options = {'edges'}

    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--gamma', dict(default=0.01, type=float)),
        ('-p', '--probability', dict(default='1/3:1/3:1/3',
                                     type=distribution)),
        ('-e', '--edges', dict(default=4, type=int)))


if __name__ == "__main__":
    bpa = BPA()
    bpa.run()
