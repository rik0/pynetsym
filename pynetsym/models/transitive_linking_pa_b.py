import functools as ft
from pynetsym.models import transitive_linking, transitive_linking_b, transitive_linking_pa


class Node(transitive_linking_b.Node, transitive_linking_pa.Node):
    pass

make_parser = transitive_linking.make_parser
make_setup = ft.partial(transitive_linking.make_setup, node_cls=Node)