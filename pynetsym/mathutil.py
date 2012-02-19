import math
import random
import networkx as nx
from numpy import cumsum, sum

def ccdf(dist):
    return 1 - (cumsum(dist, dtype=float)/sum(dist))


def estimate_s(q, delta, eps):
    delta2 = delta * delta
    delta3 = (1-delta)*(1-delta)
    return (2. / (q*q)) * math.log(2./eps) * delta3 / delta2


def approximate_cpl(graph, q=0.5, delta=0.15, eps=0.05):
    assert isinstance(graph, nx.Graph)
    s = estimate_s(q, delta, eps)
    s = int(math.ceil(s))
    if graph.number_of_nodes() <= s:
        sample = graph.nodes_iter()
    else:
        sample = random.sample(graph.adj.keys(), s)

    averages = []
    for node in sample:
        path_lengths = nx.single_source_shortest_path_length(graph, node)
        average = sum(path_lengths.itervalues())/float(len(path_lengths))
        averages.append(average)
    averages.sort()
    median_index = int(len(averages) * q + 1)
    return averages[median_index]