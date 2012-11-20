from matplotlib import pyplot as plt
from os import path
from util import make_distributions
from pynetsym import AsyncClock, BasicConfigurator
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert
import networkx as nx
import os
import time
import numpy as np
import matplotlib
import gc

from numpy import arange, save, dtype, array, savetxt
from pynetsym.util import sna

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator

class Node2(Node):
    def activate(self):
        forbidden = set()
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.random_selector.preferential_attachment()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1
            self.cooperate()

class Activator2(Activator):

    def nodes_to_create(self):
        return [(Node2, dict(starting_edges=self.starting_edges))]

class BA(barabasi_albert.BA):
    clock_type = AsyncClock
    activator_type = Activator2

    @property
    def clock_options(self):
        return dict(remaining_ticks=self.steps)

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
    directory_name = "no_sync_clock_no_sync_agent_%d" % time.time()
    os.mkdir(directory_name)

    F_pdf = plt.figure()
    F_ccdf = plt.figure()

    sim = BA()
    sim.setup_parameters(starting_edges=11, starting_network_size=11, steps=100000)
    sim.run()

    steps = sim.steps
    starting_edges = sim.starting_edges
    starting_networks_size = sim.starting_network_size

    with sim.graph.handle as graph:
        del sim; gc.collect()
        print graph.number_of_nodes(), graph.number_of_edges()

        ccdf_axes = F_ccdf.gca()
        pdf_axes = F_pdf.gca()

        degrees = graph.degree().values()
        sim_ccdf, sim_pdf = make_distributions(degrees)
        savetxt(path.join(os.curdir,
                          directory_name, 'raw_degrees.csv'),
                degrees)
        nx.write_graphml(graph, path.join(os.curdir,
                                          directory_name, 'graph.graphml'))

        cdf_xs = arange(starting_edges - 1, len(sim_ccdf))
        pdf_xs = arange(starting_edges, len(sim_pdf))

        ccdf_axes.loglog(cdf_xs, sim_ccdf[starting_edges-1:],
                         color='blue')
        pdf_axes.loglog(pdf_xs, sim_pdf[starting_edges:],
                        color='blue', marker='o', linestyle='')

    gc.collect()

    ba_graph = nx.barabasi_albert_graph(
        steps + starting_networks_size,
        starting_edges)

    ba_ccdf, ba_pdf = make_distributions(ba_graph)

    ccdf_axes.loglog(arange(starting_edges-1, len(ba_ccdf)), ba_ccdf[starting_edges-1:], color='red', linestyle='--')
    pdf_axes.loglog(arange(starting_edges, len(ba_pdf)), ba_pdf[starting_edges:], color='red', marker='+', linestyle='')

    del ba_graph
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

    data_record = dtype([('nodes', np.int), ('ab', np.float), ('nx', np.float)])

    max_cdf_size = max(len(sim_ccdf), len(ba_ccdf))
    ccdf_frame = np.zeros((max_cdf_size+1, ), dtype=data_record)

    ccdf_frame['nodes'] = arange(0, max_cdf_size+1)
    ccdf_frame['ab'][:len(sim_ccdf)] = sim_ccdf
    ccdf_frame['nx'][:len(ba_ccdf)] = ba_ccdf

    savetxt(path.join(os.curdir, directory_name, 'ccdf.csv'),
            ccdf_frame, delimiter=', ')

    max_pdf_size = max(len(sim_pdf), len(ba_pdf))
    pdf_frame = np.zeros((max_pdf_size+1, ), dtype=data_record)
    pdf_frame['nodes'] = arange(0, max_pdf_size+1)
    pdf_frame['ab'][:len(sim_pdf)] = sim_pdf
    pdf_frame['nx'][:len(ba_pdf)] = ba_pdf

    savetxt(path.join(os.curdir, directory_name, 'pdf.csv'),
            pdf_frame, delimiter=', ')

    for format in FORMATS:
        F_ccdf.savefig(path.join(os.curdir, directory_name, 'ba-ccdf.%s' % format),
                       dpi=DPI, format=format)
        F_pdf.savefig(path.join(os.curdir, directory_name, 'ba-pdf.%s' % format),
                      dpi=DPI, format=format)