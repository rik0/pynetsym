from pynetsym.models import transitive_linking, transitive_linking_b, transitive_linking_pa

make_parser = transitive_linking.make_parser
make_setup = transitive_linking.make_setup


class Node(transitive_linking_b.Node, transitive_linking_pa.Node):
    pass