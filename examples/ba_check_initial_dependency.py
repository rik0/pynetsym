import os
import time
from os import path
from matplotlib import pyplot as plt

import networkx as nx

from pynetsym.generation_models import barabasi_albert
#from . import ba_stepped2 as barabasi_albert
from pynetsym import mathutil

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA

DPI = 100
multipliers = [1, 10, 100]
markers = ['+', '*', '.']
colors = ['blue', 'green', 'cyan']

ba_color = 'red'
ba_label = 'NetworkX Barabasi Albert'
ba_marker = 'x'

if __name__ == '__main__':
    directory_name = "ba_test_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()
    ba_graph = None

    for starting_size_mul, marker, color in zip(
            multipliers, markers, colors):
        sim = BA()
        sim.setup_parameters()
        sim.run(
            starting_network_size=sim.starting_edges * starting_size_mul)

        filename = path.join(
            os.curdir,
            directory_name,
            ("%(steps)s_%(starting_network_size)s_%(starting_edges)s.graphml" %
                sim.get_parameters()))

        label = '%d starting size' % sim.starting_network_size
        steps = sim.steps
        starting_edges = sim.starting_edges
        starting_networks_size = sim.starting_network_size

        if isinstance(sim.graph.handle, nx.Graph):
            graph = sim.graph.handle
        else:
            sim.graph.handle.write(filename)
            graph = nx.read_graphml(filename)

        print graph.number_of_nodes(), graph.number_of_edges()

        del sim

        dst = mathutil.degrees_to_hist(graph.degree())
        ccdf = mathutil.ccdf(dst)

        if ba_graph is None:
            ba_graph = nx.barabasi_albert_graph(
                steps + starting_networks_size,
                starting_edges)

            print 'Agent:', graph.number_of_nodes(),
            print  graph.number_of_edges()
            print 'PB:', ba_graph.number_of_nodes(),
            print  ba_graph.number_of_edges()

            ba_dst = mathutil.degrees_to_hist(ba_graph.degree())
            F_pdf.gca().loglog(ba_dst, marker=ba_marker, color=ba_color,
                linestyle='', label=ba_label)
            ba_ccdf = mathutil.ccdf(ba_dst)
            F_ccdf.gca().loglog(ba_ccdf, color=ba_color, label=ba_label)

        F_pdf.gca().loglog(dst, marker=marker, color=color,
            linestyle='', label=label)
        F_ccdf.gca().loglog(ccdf, color=color, label=label)

    F_pdf.savefig(path.join(os.curdir, directory_name, 'dst.png'),
                dpi=DPI, format='png')
    F_ccdf.savefig(path.join(os.curdir, directory_name, 'ccdf.png'),
                dpi=DPI, format='png')

