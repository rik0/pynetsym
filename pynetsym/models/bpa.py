import pynetsym
from pynetsym import core

def inviter_distribution(node):
    pass

def passive_distribution(node):
    return

def linker_distribution(node):
    pass


class Node(core.Node):
    def __init__(self, identifier, address_book, graph, gamma, eps, p):
        super(Node, self).__init__(self, identifier, address_book, graph)
        self.gamma = gamma
        self.eps = eps
        self.p = p

    def activate(self):
        self.distribution(self,)
