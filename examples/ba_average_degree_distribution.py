"""
This script generates several BA model networks both with our generator and 
with the one included in NetworkX. Then computes the averages among all the
degree distributions and plots them (both PDF and CCDF).
"""

from matplotlib import pyplot as plt
from os import path
from pynetsym import mathutil
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert
import networkx as nx
import os
import time
import numpy as np


def average_distribution(dst):
    pad(dst)
    dst = np.vstack(dst)
    return np.average(dst, axis=0)

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA

ITERATIONS = 10
DPI = 100
markers = ['+', '*', '.']
colors = ['blue', 'green', 'cyan']

ba_color = 'red'
ba_label = 'NetworkX Barabasi Albert'
ba_marker = 'x'

def pad(seq):
    """
    Pads a sequence of arrays to make them vstackable.

    @return: None
    """
    max_ = max(el.size for el in seq)
    for el in seq:
        el.resize(max_, refcheck=False)

if __name__ == '__main__':
    directory_name = "average_comaprison_analysis_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()
    ba_graph = None

    pynetsym_ccdfs = []
    pynetsym_pdfs = []
    ba_ccdfs = []
    ba_pdfs = []

    for _iteration in xrange(ITERATIONS):
        sim = BA()
        sim.setup_parameters()
        sim.run()

        label = '%d starting size' % sim.starting_network_size
        steps = sim.steps
        starting_edges = sim.starting_edges
        starting_networks_size = sim.starting_network_size

        graph = sim.graph.handle

        del sim

        bins = np.bincount(graph.degree().values())
        ccdf = mathutil.ccdf(bins)
        pdf = np.asfarray(bins) / len(bins)

        pynetsym_ccdfs.append(ccdf)
        pynetsym_pdfs.append(pdf)

        ba_graph = nx.barabasi_albert_graph(
            steps + starting_networks_size,
            starting_edges)

        bins = np.bincount(ba_graph.degree().values())
        ccdf = mathutil.ccdf(bins)
        pdf = np.asfarray(bins) / len(bins)

        ba_ccdfs.append(ccdf)
        ba_pdfs.append(ccdf)

    ccdf_axes = F_ccdf.gca()
    pdf_axes = F_pdf.gca()

    pynetsym_avg_ccdf = average_distribution(pynetsym_ccdfs)
    ba_avg_ccdf = average_distribution(ba_ccdfs)
    pynetsym_avg_pdf = average_distribution(pynetsym_pdfs)
    ba_avg_pdf = average_distribution(ba_pdfs)

    ccdf_axes.loglog(pynetsym_avg_ccdf, color='blue', label=label)
    ccdf_axes.loglog(ba_avg_ccdf, color='red', label=label)

    F_ccdf.savefig(path.join(os.curdir, directory_name, 'ccdf.png'),
        dpi=DPI, format='png')

    pdf_axes.loglog(pynetsym_avg_pdf, color='blue', marker='+', linestyle='',
        label=label)
    pdf_axes.loglog(ba_avg_pdf, color='red', marker='x', linestyle='',
        label=label)
    F_pdf.savefig(path.join(os.curdir, directory_name, 'pdf.png'),
        dpi=DPI, format='png')


