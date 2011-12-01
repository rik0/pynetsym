import random
import itertools as it
from .. import pa_utils
from pynetsym.models import transitive_linking

make_parser = transitive_linking.make_parser
make_setup = transitive_linking.make_setup

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
            self.link_to(self.CRITERION)
