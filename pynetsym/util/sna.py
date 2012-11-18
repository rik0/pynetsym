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


def trivial_power_law_estimator(dataset, x0=None):
    if x0 is None:
        x0 = min(dataset)
        xs = dataset
    else:
        xs = [x for x in dataset if x >= x0]

    s = sum(math.log(x / x0) for x in xs)
    return 1. + len(dataset) / s


def make_hist(xs):
    vals = zeros(xs[-1] + 1, dtype=int)
    for val in xs:
        vals[val] += 1
    return vals


def degrees_to_hist(dct):
    xs = dct.values()
    xs.sort()
    vals = make_hist(xs)
    return vals
