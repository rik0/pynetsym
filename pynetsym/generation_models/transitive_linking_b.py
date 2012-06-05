import random
import itertools as it

from pynetsym.generation_models import transitive_linking
from pynetsym import simulation
from pynetsym import node_manager


class Node(transitive_linking.Node):
    def find_possible_links(self, graph, neighbors):
        possible_links = [link for link in it.combinations(neighbors, 2)
                          if not graph.has_edge(*link)]
        return possible_links

    def introduce(self):
        graph = self.graph.handle
        neighbors = graph.neighbors(self.id)

        possible_links = self.find_possible_links(graph, neighbors)
        if possible_links:
            node_a, node_b = random.choice(possible_links)
            self.send(node_a, 'introduce_to', target_node=node_b)
        else:
            self.link_to(self.criterion)


class TL(simulation.Simulation):
    command_line_options = (
        ('-n', '--starting-network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=lambda graph: graph.preferential_attachment_node(),
            default=lambda graph: graph.random_node())))

    class configurator_type(node_manager.BasicConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}


if __name__ == '__main__':
    sim = TL()
    sim.run()
