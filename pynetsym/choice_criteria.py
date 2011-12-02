import rnd

def preferential_attachment(graph):
    if graph.number_of_edges():
        return rnd.random_edge(graph)[0]
    else:
        return rnd.random_node(graph)
