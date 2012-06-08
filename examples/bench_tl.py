from pynetsym.generation_models import transitive_linking
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it


NETWORK_SIZES = [100, 500, 1000, 2000]


fig = plt.figure(0)
ax_xpos = it.cycle([1, 2])
ax_ypos = it.count()

for sns in NETWORK_SIZES:
    ax = fig.add_subplot(
        len(NETWORK_SIZES),
        next(ax_xpos),
        next(ax_ypos))

    sim = transitive_linking.TL()
    sim.run(starting_network_size=sns, steps=10000)
    graph = sim.graph.handle
    del sim

    print 'Nodes:', graph.number_of_nodes()
    print 'Edges:', graph.number_of_edges()
    print 'CC:', nx.average_clustering(graph)

    nx.draw(graph, ax=ax)

plt.show()

