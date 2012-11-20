from matplotlib import pyplot as plt
from os import path
from pynetsym import node_manager, BasicConfigurator
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert
import networkx as nx
import os
import time
import numpy as np
import matplotlib
import gc

from numpy import arange
from pynetsym.util import sna


def plot_simulation(sim, ccdf_axes, pdf_axes, color, marker, linestyle):
    sim.setup_parameters(starting_edges=11, starting_network_size=11, steps=100000)
    sim.run()
    steps = sim.steps
    starting_edges = sim.starting_edges
    starting_networks_size = sim.starting_network_size
    graph = sim.graph.handle
    del sim
    gc.collect()
    sim_ccdf, sim_pdf = make_distributions(graph)
    del graph
    ccdf_axes.loglog(arange(starting_edges - 1, len(sim_ccdf)), sim_ccdf[starting_edges - 1:], color=color, linestyle=linestyle)
    pdf_axes.loglog(arange(starting_edges, len(sim_pdf)), sim_pdf[starting_edges:], color=color, marker=marker, linestyle='')
    del sim_ccdf
    del sim_pdf
    gc.collect()
    return steps, starting_edges

def make_distributions(graph):
    bins = np.bincount(graph.degree().values())
    ccdf = sna.ccdf(bins)
    pdf = np.asfarray(bins) / np.sum(bins)
    return ccdf, pdf

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA


class Node2(Node):
    def activate(self):
        forbidden = set()
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.preferential_attachment_node()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1
            self.cooperate()

class Activator2(Activator):

    def nodes_to_create(self):
        return [(Node2, dict(starting_edges=self.starting_edges))]


class BA2(BA):
    activator_type = Activator2

    class configurator_type(BasicConfigurator):
        node_type = Node2
        node_options = {'starting_edges'}

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
    directory_name = "compare_handler_distribution_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()

    ccdf_axes = F_ccdf.gca()
    pdf_axes = F_pdf.gca()


    sim = BA()
    steps, starting_edges = plot_simulation(sim, ccdf_axes, pdf_axes, 'blue', 'o', '-')
    sim2 = BA2()
    plot_simulation(sim2, ccdf_axes, pdf_axes, 'red', '+', '--')

    ccdf_axes.set_title('CCDF BA(%d, %d)' % (steps, starting_edges))
    ccdf_axes.legend(('Not-Interruptible Handler', 'Interruptible Handler'), loc='best')
    ccdf_axes.set_xlabel('Degree $x$')
    ccdf_axes.set_ylabel('Probability')
    ccdf_axes.set_xlim(left=starting_edges-1)
    ccdf_axes.grid(True)

    pdf_axes.set_title('PMF BA(%d, %d)' % (steps, starting_edges))
    pdf_axes.legend(('Not-Interruptible Handler', 'Interruptible Handler'), loc='best')
    pdf_axes.set_xlabel('Degree $x$')
    pdf_axes.set_ylabel('Probability')
    pdf_axes.set_xlim(left=starting_edges-1)
    pdf_axes.grid(True)


    F_ccdf.tight_layout(pad=0.4)
    F_pdf.tight_layout(pad=0.4)

    for format in FORMATS:
        F_ccdf.savefig(path.join(os.curdir, directory_name, 'ba-handler-ccdf.%s' % format),
                       dpi=DPI, format=format)
        F_pdf.savefig(path.join(os.curdir, directory_name, 'ba-handler-pdf.%s' % format),
                      dpi=DPI, format=format)


