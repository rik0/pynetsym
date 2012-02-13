import random
import string
import itertools as it

def _iter_random_choice(iterator, max_value):
    chosen_index = random.randrange(0, max_value)
    for index, item in enumerate(iterator):
        if index == chosen_index:
            return item


def random_edge(graph):
    """Draw a random edge from the graph.

    Returns (node_id, node_id) pair or None if the graph has no edges.

    This is relatively safe, although horribly slow."""
    return _iter_random_choice(
        graph.edges_iter(),
        graph.number_of_edges())


def random_node(graph):
    """Draw a random node from the graph.

    Returns a node index or None if the graph has no nodes.

    Notice that it assumes that the graph nodes have indices going from 0 to some n.
    If it is not the case, the draw may not be uniform, bugs may arise, demons may
    fly out of your node.
    """
    max_value = graph.number_of_nodes()
    chosen_index = random.randrange(0, max_value)
    if graph.has_node(chosen_index):
        return chosen_index
    else:
        return _iter_random_choice(
            graph.nodes_iter(),
            max_value)

def random_printable_chars():
    """
    Yield an infinite sequence of printable characters.

    """
    while 1:
        yield random.choice(string.printable)