import math
import random
from numpy import cumsum, sum, zeros


def ccdf(dist):
    return 1 - (cumsum(dist, dtype=float) / sum(dist))

def _estimate_s(q, delta, eps):
    delta2 = delta * delta
    delta3 = (1 - delta) * (1 - delta)
    return (2. / (q * q)) * math.log(2. / eps) * delta3 / delta2

def approximate_cpl(graph, q=0.5, delta=0.15, eps=0.05):
    """
    Computes the approximate CPL for the specified graph
    :param graph: the graph
    :param q: the q-median to use (default 1/2-median, i.e., median)
    :param delta: used to compute the size of the sample
    :param eps: used to compute the size of the sample
    :return: the median
    :rtype: float
    """
    import networkx
    assert isinstance(graph, networkx.Graph)
    s = _estimate_s(q, delta, eps)
    s = int(math.ceil(s))
    if graph.number_of_nodes() <= s:
        sample = graph.nodes_iter()
    else:
        sample = random.sample(graph.adj.keys(), s)

    averages = []
    for node in sample:
        path_lengths = networkx.single_source_shortest_path_length(graph, node)
        average = sum(path_lengths.values()) / float(len(path_lengths))
        averages.append(average)
    averages.sort()
    median_index = int(len(averages) * q + 1)
    return averages[median_index]

def trivial_power_law_estimator(data, x0=None):
    if x0 is None:
        x0 = min(data)
        xs = data
    else:
        xs = [x for x in data if x >= x0]

    s = sum(math.log(x / x0) for x in xs)
    return 1. + len(data) / s

def make_hist(xs):
    values = zeros(xs[-1] + 1, dtype=int)
    for val in xs:
        values[val] += 1
    return values


def degrees_to_hist(dct):
    xs = dct.values()
    xs.sort()
    values = make_hist(xs)
    return values
