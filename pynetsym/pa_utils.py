import rnd

__author__ = 'enrico'

def preferential_attachment(graph, sample_size=1):
    for _iteration in xrange(sample_size):
        edge = rnd.random_edge(graph)
        if edge is None:
            yield rnd.random_node(graph)
        else:
            yield edge[0]