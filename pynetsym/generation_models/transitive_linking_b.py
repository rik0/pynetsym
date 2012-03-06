import random
import itertools as it

from . import transitive_linking
from pynetsym import simulation, rnd, choice_criteria, node_manager

class Node(transitive_linking.Node):
    def find_possible_links(self, graph, neighbors):
        possible_links = [link for link in it.combinations(neighbors, 2)
                          if not graph.has_edge(*link)]
        return possible_links

    def introduce(self):
        graph = self.graph
        neighbors = graph.neighbors(self.id)

        possible_links = self.find_possible_links(graph, neighbors)
        if possible_links:
            node_a, node_b = random.choice(possible_links)
            self.send(node_a, 'introduce_to', target_node=node_b)
        else:
            self.link_to(self.criterion)


class TL(simulation.Simulation):
    simulation_options = (
        ('-n', '--network-size', dict(default=100, type=int)),
        ('--death-probability', dict(default=0.01, type=float)),
        ('--preferential-attachment', dict(
            dest='criterion', action='store_const',
            const=choice_criteria.preferential_attachment,
            default=rnd.random_node)))

    class configurator(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {"death_probability", "criterion"}
        activator_options = {}



