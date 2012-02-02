import networkx as nx
import csv

def make_sw_graph(fobj, n, k, rng):
    writer = csv.writer(fobj)
    writer.writerow(('p', 'CPL', 'C'))

    for p in rng:
        graph = nx.watts_strogatz_graph(n, k, p)
        writer.writerow((
            p,
            nx.average_shortest_path_length(graph),
            nx.average_clustering(graph)))
