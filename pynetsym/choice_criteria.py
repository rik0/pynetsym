import random
import pynetsym


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
        return pynetsym.rnd.choice_from_iter(
            graph.nodes_iter(),
            max_value)

def random_edge(graph):
    """
    Draw a random edge from the graph.

    Returns (node_id, node_id) pair or None if the graph has no edges.

    This is relatively safe, although horribly slow.
    """
    return pynetsym.rnd.choice_from_iter(
        graph.edges_iter(),
        graph.number_of_edges())

def preferential_attachment_edge(graph):
    if graph.number_of_edges():
        return random_edge(graph)[0]
    else:
        return random_node(graph)


def preferential_attachment(graph):
    m = graph.number_of_edges() + graph.number_of_nodes()
    while 1:
        n = random_node(graph)
        k = graph.degree(n) + 1
        p = float(k) / m
        if random.random() < p:
            return n

def preferential_attachment0(graph):
    m = graph.number_of_edges()
    while 1:
        n = random_node(graph)
        k = graph.degree(n)
        p = float(k) / m
        if random.random() < p:
            return n
