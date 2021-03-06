from matplotlib import pyplot as plt
from os import path
import networkx as nx
import os
import time
import numpy as np
import itertools as it

#from . import ba_stepped2 as barabasi_albert
from pynetsym.util import sna


def average_distribution(dst):
    pad(dst)
    dst = np.vstack(dst)
    return np.average(dst, axis=0)


ITERATIONS = 10
STEPS = 100
DPI = 100
markers = it.cycle(['+', '*', '.'])
colors = ['blue', 'green', 'cyan', '0.75', 'black', '0.5', '#FF8080',
    '#56F712', '#10EE62', '#848484']

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
    directory_name = "multi_nx_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()
    ba_graph = None

    ba_ccdfs = []
    ba_pdfs = []

    for _iteration in xrange(ITERATIONS):
        ba_graph = nx.barabasi_albert_graph(STEPS, 5)

        bins = np.bincount(ba_graph.degree().values())
        ccdf = sna.ccdf(bins)
        pdf = np.asfarray(bins) / len(bins)

        ba_ccdfs.append(ccdf)
        ba_pdfs.append(ccdf)

    ccdf_axes = F_ccdf.gca()
    pdf_axes = F_pdf.gca()

    for dst, color in zip(ba_ccdfs, colors):
        ccdf_axes.loglog(dst, color=color)

    #ba_avg_ccdf = average_distribution(ba_ccdfs)
    #ccdf_axes.loglog(ba_avg_ccdf, color='red')

    F_ccdf.savefig(path.join(os.curdir, directory_name, 'ccdf.png'),
        dpi=DPI, format='png')

    for dst, color, marker in zip(ba_pdfs, colors, markers):
        pdf_axes.loglog(dst, color=color, marker=marker, linestyle='')

    #ba_avg_pdf = average_distribution(ba_pdfs)
    #pdf_axes.loglog(ba_avg_pdf, color='red', marker='x', linestyle='')

    F_pdf.savefig(path.join(os.curdir, directory_name, 'pdf.png'),
        dpi=DPI, format='png')
