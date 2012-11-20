import networkx as nx

from pynetsym import core, configurators, simulation

from pympler.classtracker import ClassTracker
from pympler import tracker
from pympler import muppy


# trck = ClassTracker()
from pynetsym.nodes import Node

st = tracker.SummaryTracker()

class Node(Node):
    def activate(self):
        pass

class Simulation(simulation.Simulation):
    class configurator_type(configurators.NXGraphConfigurator):
        node_type = Node
        node_options = {}


# trck.track_class(core.Agent, resolution_level=5)
# trck.track_class(Node, resolution_level=5)

st.print_diff()
g = nx.powerlaw_cluster_graph(5000, 20, 0.1)
# trck.track_object(g, resolution_level=5)
# trck.create_snapshot('Graph only')

st.print_diff()

sim = Simulation()
sim.run(starting_graph=g)
st.print_diff()
# trck.create_snapshot('With agents')
# trck.stats.print_summary()


from pympler import refbrowser
import types

def output_function(o):
    return str(type(o))

for root in muppy.filter(muppy.get_objects(), types.MethodType):
    refbrowser.ConsoleBrowser(root, maxdepth=2,
            str_func=output_function).print_tree()


