import random
import rnd

def preferential_attachment_edge(graph):
    if graph.number_of_edges():
        return rnd.random_edge(graph)[0]
    else:
        return rnd.random_node(graph)


def preferential_attachment(graph):
    m = graph.number_of_edges() + graph.number_of_nodes()
    while 1:
        n = rnd.random_node(graph)
        k = graph.degree(n) + 1
        p = float(k) / m
        if random.random() < p:
            return n

def preferential_attachment0(graph):
    m = graph.number_of_edges()
    while 1:
        n = rnd.random_node(graph)
        k = graph.degree(n)
        p = float(k) / m
        if random.random() < p:
            return n
