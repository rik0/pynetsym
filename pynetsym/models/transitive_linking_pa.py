import functools as ft
from pynetsym import choice_criteria
from pynetsym.models import transitive_linking

class Node(transitive_linking.Node):
    def __init__(self, identifier, address_book, graph, death_probability):
        self.criterion = choice_criteria.preferential_attachment
        super(Node, self).__init__(identifier, address_book, graph, death_probability)

make_parser = transitive_linking.make_parser
make_setup = ft.partial(transitive_linking.make_setup, node_cls=Node)
