import random

def iter_random_choice(iterator, max_value):
    chosen_index = random.randint(0, max_value)
    for index, item in enumerate(iterator):
        if index == chosen_index:
            return item


def random_edge(graph):
    return iter_random_choice(
        graph.edges_iter(),
        graph.number_of_edges())


def random_node(graph):
    max_value = graph.number_of_nodes()
    chosen_index = random.randint(0, max_value)
    if graph.has_node(chosen_index):
        return chosen_index
    else:
        return iter_random_choice(
            graph.nodes_iter(),
            max_value)