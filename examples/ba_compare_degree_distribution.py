from matplotlib import pyplot as plt
from os import path
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert
import networkx as nx
import os
import time
import numpy as np
import matplotlib
import gc

from numpy import arange
from pynetsym.util import sna


def make_distributions(graph):
    bins = np.bincount(graph.degree().values())
    ccdf = sna.ccdf(bins)
    pdf = np.asfarray(bins) / np.sum(bins)
    return ccdf, pdf

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA

DPI = 1000
FORMATS = [
    'pdf',
    'eps',
]
markers = ['+', '*', '.']
colors = ['blue', 'green', 'cyan']

ba_color = 'red'
ba_label = 'NetworkX Barabasi Albert'
ba_marker = 'x'

font_properties = {
    #'size': 48
}

matplotlib.rc('font', size=20)



if __name__ == '__main__':
    directory_name = "compare_degree_distribution_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()

    sim = BA()
    sim.setup_parameters(starting_edges=11, starting_network_size=11, steps=5000)
    sim.run()

    steps = sim.steps
    starting_edges = sim.starting_edges
    starting_networks_size = sim.starting_network_size

    graph = sim.graph.handle

    del sim; gc.collect()

    ccdf_axes = F_ccdf.gca()
    pdf_axes = F_pdf.gca()

    sim_ccdf, sim_pdf = make_distributions(graph)
    ccdf_axes.loglog(arange(starting_edges-1, len(sim_ccdf)), sim_ccdf[starting_edges-1:], color='blue')
    pdf_axes.loglog(arange(starting_edges, len(sim_pdf)), sim_pdf[starting_edges:], color='blue', marker='o', linestyle='')

    del graph
    del sim_ccdf
    del sim_pdf
    gc.collect()

    ba_graph = nx.barabasi_albert_graph(
        steps + starting_networks_size,
        starting_edges)

    ba_ccdf, ba_pdf = make_distributions(ba_graph)

    ccdf_axes.loglog(arange(starting_edges-1, len(ba_ccdf)), ba_ccdf[starting_edges-1:], color='red', linestyle='--')
    pdf_axes.loglog(arange(starting_edges, len(ba_pdf)), ba_pdf[starting_edges:], color='red', marker='+', linestyle='')

    del ba_graph
    del ba_ccdf
    del ba_pdf
    gc.collect()

    ccdf_axes.set_title('CCDF BA(%d, %d)' % (steps, starting_edges))
    ccdf_axes.legend(('Agent-Based', 'NetworkX'), loc='best')
    ccdf_axes.set_xlabel('Degree $x$')
    ccdf_axes.set_ylabel('Probability')
    ccdf_axes.set_xlim(left=starting_edges-1)
    ccdf_axes.grid(True)

    pdf_axes.set_title('PMF BA(%d, %d)' % (steps, starting_edges))
    pdf_axes.legend(('Agent-Based', 'NetworkX'), loc='best')
    pdf_axes.set_xlabel('Degree $x$')
    pdf_axes.set_ylabel('Probability')
    pdf_axes.set_xlim(left=starting_edges-1)
    pdf_axes.grid(True)


    F_ccdf.tight_layout(pad=0.4)
    F_pdf.tight_layout(pad=0.4)

    for format in FORMATS:
        F_ccdf.savefig(path.join(os.curdir, directory_name, 'ba-ccdf.%s' % format),
                       dpi=DPI, format=format)
        F_pdf.savefig(path.join(os.curdir, directory_name, 'ba-pdf.%s' % format),
                      dpi=DPI, format=format)


