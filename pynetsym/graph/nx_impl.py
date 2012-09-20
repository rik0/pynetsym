from  . import interface
import networkx as nx
from traits.api import HasTraits, Instance
from traits.api import DelegatesTo


class NxGraph(HasTraits):
    nx_graph = Instance(nx.Graph, allow_none=False)

    number_of_nodes = DelegatesTo('nx_graph')
    number_of_edges = DelegatesTo('nx_graph')



    def __init__(self, graph_type=nx.Graph, data=None, **kwargs):
        self.nx_graph = graph_type(data=data, **kwargs)

    def add_node(self, node):
        self.nx_graph.add_node(node)

    def add_edge(self, source, target):
        self.nx_graph.add_edge(source, target)

    def remove_edge(self, source, target):
        self.nx_graph.remove_edge(source, target)

