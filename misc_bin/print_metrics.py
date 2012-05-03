import argparse

import networkx as nx

from os import path

# TODO: decide what to do
from matplotlib import pyplot as plt
import pynetsym


FORMATS = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')
"""Available formats"""

def read_network(network_path, fmt=None, **kwargs):
    """
    Reads a network from filesystem.
    @param network_path: The file to read the network from
    @param fmt: the format the network was stored in (some kind of guessing is
        made from the filename, if left blank)
    @param kwargs: Additional arguments to be passed to the corresponding
        networkx.read_* function
    @return: the network
    @rtype: networkx.Graph
    """
    if fmt is None:
        _, ext = path.splitext(network_path)
        fmt = ext[1:]
        if fmt not in FORMATS:
            raise IOError("Did not undestand format from filename %s." % network_path)
    fn = getattr(nx, 'read_' + fmt)
    return fn(network_path, **kwargs)

def build_parser():
    parser = argparse.ArgumentParser(
        description='Simple Network Analyzer' )
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
        ccdf = pynetsym.mathutil.ccdf(hst)
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
        G = read_network(network_path)
        process_network(G, namespace)



if __name__ == '__main__':
    parser = build_parser()
    namespace = parser.parse_args()
    main(namespace)

