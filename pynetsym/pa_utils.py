import rnd

__author__ = 'enrico'

def preferential_attachment(graph, sample_size=1):
    for _iteration in xrange(sample_size):
        if graph.number_of_edges():
            yield rnd.random_edge(graph)[0]
        else:
            yield rnd.random_node(graph)
