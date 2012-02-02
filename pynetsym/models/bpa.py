import argparse
import fractions

import itertools as it
import random

from pynetsym import core

def distribution(s):
    parts =  [fractions.Fraction(part) for part in s.split(':')]
    if sum(parts) != 1:
        raise ValueError('Distribution components sum to one.')
    elif len(parts) != 3:
        raise ValueError('Distribution should have three events.')
    else:
        return tuple(float(f) for f in parts)


class Node(core.Node):
    def __init__(self, identifier, address_book, graph, gamma, edges, probability):
        super(Node, self).__init__(identifier, address_book, graph)
        self.gamma = gamma
        self.eps = edges
        self.p = probability
        self.distribution = self._select_distribution()

    def _select_distribution(self):
        random_value = random.random()
        if random_value < self.p[0]:
           return self.linker_distribution
        elif random_value < self.p[0] + self.p[1]:
            return self.inviter_distribution
        else:
            return self.passive_distribution

    def activate(self):
        node = self.distribution()
        if node is not None:
            self.send(node, 'accept_link', originating_node=self.id)

    def inviter_distribution(self):
        pass

    def passive_distribution(self):
        return

    def linker_distribution(self):
        pass



def make_parser(parent):
    parser = argparse.ArgumentParser(parents=[parent,])
    parser.add_argument('-n', '--network-size', default=100, type=int)
    parser.add_argument('--gamma', default=0.01, type=float)
    parser.add_argument('-p', '--probability', default='1/3:1/3:1/3', type=distribution)
    parser.add_argument('-e', '--edges', default=4, type=int)

    return parser

def make_setup(network_size, gamma, edges, probability, node_cls=Node):
    def setup(node_manager):
        generation_seed = it.izip(
            it.repeat(node_cls),
            xrange(network_size),
            it.repeat(
                dict(
                    gamma=gamma,
                    edges=edges,
                    probability=probability)))
        for cls, identifier, node_params in generation_seed:
            node_manager.create_node(cls, identifier, node_params)

    return setup