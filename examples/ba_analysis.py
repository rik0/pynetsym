import os
import time
from os import path
from matplotlib import pyplot as plt

import networkx as nx

from pynetsym.generation_models import barabasi_albert
from pynetsym import mathutil

Node = barabasi_albert.Node
Activator = barabasi_albert.Activator
BA = barabasi_albert.BA

multipliers = [1, 10, 100, 1000]
markers = ['+', 'x', '*', '.']
colors = ['blue', 'red', 'green', 'cyan']

if __name__ == '__main__':
    directory_name = "ba_test_%d" % time.time()
    os.mkdir(directory_name)

    F = plt.figure(figsize=(10, 4))

    for starting_size_multiplier, marker, color in zip(
            multipliers, markers, colors):
        sim = BA()
        sim.setup_parameters()
        sim.run(network_size=sim.starting_edges * starting_size_multiplier)

        filename = path.join(
            os.curdir,
            directory_name,
            "%(steps)s_%(network_size)s_%(starting_edges)s.graphml" % vars(sim))
        sim.graph.handle.write(filename)

        label = '%d starting size' % sim.network_size
        del sim

        graph = nx.read_graphml(filename)
        dst = mathutil.degrees_to_hist(graph.degree())
        ccdf = mathutil.ccdf(dst)

        plt.subplot(121)
        plt.loglog(dst, marker=marker, color=color, linestyle='',
            label=label)

        plt.subplot(122)
        plt.loglog(ccdf, color=color, label=label)

    plt.subplot(121)
    plt.legend()
    plt.savefig(path.join(os.curdir, directory_name, 'plt.png'),
                dpi=1000, format='png')
    
