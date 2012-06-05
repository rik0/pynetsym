from matplotlib import pyplot as plt
from os import path
from pynetsym import mathutil
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert
import numpy as np
import os
import time
import itertools as it
import matplotlib


#from . import ba_stepped2 as barabasi_albert


def average_distribution(dst):
    pad(dst)
    dst = np.vstack(dst)
    return np.average(dst, axis=0)


ITERATIONS = 10
STEPS = 10000
DPI = 1000
FORMATS = [
    'pdf',
    'eps',
]

markers = it.cycle(['+', '*', '.', 'x', 'o'])
colors = ['blue', 'green', 'cyan', '0.75', 'black', '0.5', '#FF8080',
    '#56F712', '#10EE62', '#848484']

ba_color = 'red'
ba_label = 'NetworkX Barabasi Albert'
ba_marker = 'x'

matplotlib.rc('font', size=20)

def pad(seq):
    """
    Pads a sequence of arrays to make them vstackable.

    @return: None
    """
    max_ = max(el.size for el in seq)
    for el in seq:
        el.resize(max_, refcheck=False)

if __name__ == '__main__':
    directory_name = "multi_ba_sim_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()

    ba_ccdfs = []
    ba_pdfs = []

    for _iteration in xrange(ITERATIONS):
        sim = barabasi_albert.BA()
        sim.setup_parameters(starting_edges=11, starting_network_size=11, steps=STEPS)
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

        ba_ccdfs.append(ccdf)
        ba_pdfs.append(pdf)

    ccdf_axes = F_ccdf.gca()
    pdf_axes = F_pdf.gca()

    for dst, color in zip(ba_ccdfs, colors):
        ccdf_axes.loglog(dst, color=color)
        
    #ccdf_axes.loglog(ba_avg_ccdf, color='red')

    ccdf_axes.set_title('CCDF BA(%d, %d)' % (steps, starting_edges))
    ccdf_axes.set_xlabel('Degree $x$')
    ccdf_axes.set_ylabel('Probability')
    ccdf_axes.set_xlim(left=starting_edges-1)
    ccdf_axes.grid(True)

    for dst, color, marker in zip(ba_pdfs, colors, markers):
        pdf_axes.loglog(dst, color=color, marker=marker, linestyle='')
        
    pdf_axes.set_title('PMF BA(%d, %d)' % (steps, starting_edges))
    pdf_axes.set_xlabel('Degree $x$')
    pdf_axes.set_ylabel('Probability')
    pdf_axes.set_xlim(left=starting_edges-1)
    pdf_axes.grid(True)
    

    #pdf_axes.loglog(ba_avg_pdf, color='red', marker='x', linestyle='')
    
    F_ccdf.tight_layout(pad=0.4)
    F_pdf.tight_layout(pad=0.4)
    
    for format in FORMATS:
        F_ccdf.savefig(path.join(os.curdir, directory_name, 'multi-ccdf.%s' % format),
                       dpi=DPI, format=format)
        F_pdf.savefig(path.join(os.curdir, directory_name, 'multi-pdf.%s' % format),
                      dpi=DPI, format=format)

