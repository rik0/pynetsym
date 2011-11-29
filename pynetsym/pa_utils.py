from pynetsym.rnd import random_edge, random_node

__author__ = 'enrico'

def preferential_attachment(graph, sample_size=1):
    for _iteration in xrange(sample_size):
        edge = random_edge(graph)
        if edge is None:
            yield random_node(graph)
        else:
            yield edge[0]