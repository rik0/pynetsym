from pynetsym.generation_models import nx_barabasi_albert as ba
from pynetsym import core, simulation

import networkx as nx

from pympler import tracker, classtracker, muppy, refbrowser, asizeof
import objgraph
import pynetsym


# clt = classtracker.ClassTracker()

# clt.track_class(core.Agent, resolution_level=4)
# clt.track_class(nx.Graph, resolution_level=4)
# clt.track_class(core.Node, resolution_level=4)
# clt.track_class(ba.Node, resolution_level=4)
# clt.track_class(core.Message, resolution_level=2)

# clt.create_snapshot('origin')
sim = ba.BA()
sim.run(
        starting_network_size=8,
        starting_edges=8,
        steps=10000)
# clt.create_snapshot('run')
