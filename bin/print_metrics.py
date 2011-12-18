import sys
import argparse
import matplotlib

import numpy as np
import networkx as nx

from pynetsym import io
from matplotlib import pyplot as plt


def build_parser():
    parser = argparse.ArgumentParser(
        add_help=True,
        description='Simple Network Analyzer'
    )
    parser.add_argument('--clustering-coefficient', action='store_true',
            default=True)
    parser.add_argument('--components', action='store_true',
            default=True)
    parser.add_argument('--component-size', action='store_const',
            default=0.1, type=float)
    parser.add_argument('--cpl', action='store_true', default=True)
    parser.add_argument('--approximate-cpl', action='store_true',
            default=False)
    parser.add_argument('--diameter', action='store_true', default=True)
    parser.add_argument('--assortativity', action='store_true',
            default=True)
    parser.add_argument('--degree-distribution', action='store_true',
            default=True)
    parser.add_argument('--degree-distribution-out',
            action='store_const', default=None)
    parser.add_argument('paths', metavar='paths', type=str, nargs='+')

    return parser

def process_network(G, namespace):
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
            print 'Approximate CPL not implemented.'
        if components is None:
            components = nx.connected_component_subgraphs(G)
            for i, g in enumerate(g for g in components if
                    float(len(g))/float(len(G)) >
                    namespace.component_size):
                print 'CPL %d: (%f)' % (i, float(len(g))/float(len(G)))
                print nx.average_shortest_path_length(g)
    if namespace.assortativity:
        print 'Assortativity: NOT IMPLEMENTED.'
    if namespace.degree_distribution:
        hst = nx.degree_histogram(G)

        plt.xscale('log')
        plt.yscale('log')
        plt.title("Degree Distribution")
        plt.ylabel("count")
        plt.xlabel("Degree")
        plt.plot(range(len(hst)), hst)

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
