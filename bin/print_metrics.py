import sys
import argparse
import matplotlib
import math
import random

import numpy as np
import networkx as nx

from pynetsym import io
from matplotlib import pyplot as plt

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


def ccdf_from_hst(hst):
    hst = np.array(hst, dtype=float)
    sm = np.sum(hst)
    A = np.vstack(hst for _ in hst)
    L = np.triu(A)
    return np.sum(L, axis=1)/sm

def build_parser():
    parser = argparse.ArgumentParser(
        add_help=True,
        description='Simple Network Analyzer'
    )
    parser.add_argument('--clustering-coefficient', action='store_true',
            default=True)
    parser.add_argument('--components', action='store_true',
            default=True)
    parser.add_argument('--component-size', default=0.1, type=float)
    parser.add_argument('--cpl', action='store_true', default=True)
    parser.add_argument('--approximate-cpl', default=False, type=bool)
    parser.add_argument('--diameter', action='store_true', default=True)
    parser.add_argument('--assortativity', action='store_true',
            default=True)
    parser.add_argument('--degree-distribution', action='store_true',
            default=True)
    parser.add_argument('--degree-distribution-out', default=None)
    parser.add_argument('paths', metavar='paths', type=str, nargs='+')

    return parser

def process_network(G, namespace):
    print 'Nodes:', len(G)
    print 'Edges:', G.number_of_edges()
    if namespace.clustering_coefficient:
        print 'Clustering Coefficient:', nx.average_clustering(G)
    if namespace.components:
        components = nx.connected_component_subgraphs(G)
        print 'Number of Components:', len(components)
        isles = [c for c in components if len(c) == 1]
        print 'Isles:', len(isles)
        print 'Largest Component Size:', len(components[0])
    else: components = None
    if namespace.cpl:
        if namespace.approximate_cpl:
            average_shortest_path_length = approximate_cpl
        else:
            print 'Using full slow CPL'
            average_shortest_path_length = nx.average_shortest_path_length
        if components is None:
            components = nx.connected_component_subgraphs(G)
        for i, g in enumerate(g for g in components if
                float(len(g))/float(len(G)) >
                namespace.component_size):
            print 'CPL %d: (%f)' % (i, float(len(g))/float(len(G)))
            print average_shortest_path_length(g)
    if namespace.assortativity:
        print 'Assortativity: NOT IMPLEMENTED.'
    if namespace.degree_distribution:
        hst = nx.degree_histogram(G)

        plt.subplot(121)
        plt.xscale('log')
        plt.yscale('log')
        plt.title("Degree Distribution")
        plt.ylabel("Occurrencies")
        plt.xlabel("Degree")
        plt.plot(range(len(hst)), hst, marker='+')

        plt.subplot(122)
        ccdf = ccdf_from_hst(hst)
        plt.xscale('log')
        plt.yscale('log')
        plt.title("CCDF Degree Distribution")
        plt.ylabel("$P(X>x)$")
        plt.xlabel("Degree")
        plt.plot(range(len(ccdf)), ccdf, color='red')

        if namespace.degree_distribution_out is None:
            plt.show()
        else:
            plt.save_fig(namespace.degree_distribution_out)



def main(namespace):
    for network_path in namespace.paths:
        G = io.read_network(network_path)
        process_network(G, namespace)



if __name__ == '__main__':
    parser = build_parser()
    namespace = parser.parse_args()
    main(namespace)
