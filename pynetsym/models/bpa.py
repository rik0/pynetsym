import argparse
import fractions

import itertools as it
import random
import generation

from pynetsym import core

identifiers = it.count()

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
        super(Node, self).__init__(identifier, address_book, graph)
        self.gamma = gamma
        self.p = probability
        if strategy is None:
            self.strategy = self._select_strategy()
        else:
            self.strategy = strategy

    def _select_strategy(self):
        random_value = random.random()
        if random_value < self.p[0]:
            return self.linker_strategy
        elif random_value < self.p[0] + self.p[1]:
            return self.inviter_strategy
        else:
            return self.passive_strategy

    def activate(self):
        self.strategy()

    def passive_strategy(self):
        pass

    def inviter_strategy(self):
        identifier = identifiers.next()
        self.send(
            core.NodeManager.name, 'create_node', cls=Node,
            identifier=identifier,
            parameters=dict(
                gamma=self.gamma, property=self.p,
                strategy=Node.passive_strategy))
        self.send(identifier, 'accept_link', originating_node=self.id)

    def linker_strategy(self):
        pass


class Activator(generation.Activator):
    pass


class Configurator(generation.SingleNodeConfigurator):
    identifiers_seed = identifiers
    node_cls = Node
    node_options = {'probability', 'gamma'}
    activator_cls = Activator
    activator_options = {'edges'}


def make_parser(parent):
    parser = argparse.ArgumentParser(parents=[parent, ])
    parser.add_argument('-n', '--network-size', default=100, type=int)
    parser.add_argument('--gamma', default=0.01, type=float)
    parser.add_argument('-p', '--probability', default='1/3:1/3:1/3',
        type=distribution)
    parser.add_argument('-e', '--edges', default=4, type=int)

    return parser
