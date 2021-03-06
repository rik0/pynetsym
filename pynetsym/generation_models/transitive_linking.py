"""
Transitive linking model.

Davidsen J, Ebel H, Bornholdt S (2002) Emergence of a small world from local interactions: modeling
acquaintance networks. Phys Rev Lett 88(12):1-4
"""

from traits.trait_types import Float, Trait

import random

from pynetsym import Node, Simulation, BasicConfigurator


def select_preferential_attachment(graph):
    return graph.random_selector.preferential_attachment_node()

def select_uniform(graph):
    return graph.random_selector.random_node()

class Node(Node):
    MAX_TRIALS = 10

    death_probability = Float

    criterion = Trait('uniform',
                      {'uniform': select_uniform,
                       'preferential_attachment': select_preferential_attachment},)

    def can_be_collected(self):
        return True

    def introduction(self):
        with self.graph.handle as graph:
            neighbors = graph.neighbors(self.id)
            if len(neighbors) > 1:
                for _ in xrange(self.MAX_TRIALS):
                    node_a, node_b = random.sample(neighbors, 2)
                    if not graph.has_edge(node_a, node_b):
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
        return id

    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        target_node = self.graph.random_selector.random_node()
        self.link_to(target_node)


class TL(Simulation):
    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const='preferential_attachment',
            default='uniform')))

    class configurator_type(BasicConfigurator):
        node_type = Node
        node_options = {"death_probability", "criterion"}


if __name__ == '__main__':
    sim = TL()
    sim.run()
