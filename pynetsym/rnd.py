import random

__author__ = 'enrico'

def iter_random_choice(iterator, max_value):
    choosen_index = random.randint(0, max_value)
    for index, item in enumerate(iterator):
        if index == choosen_index:
            return item


def random_edge(graph):
    return iter_random_choice(
            graph.edges_iter(),
            graph.number_of_edges())


def random_node(graph):
    return iter_random_choice(
            graph.nodes_iter(),
            graph.number_of_nodes())