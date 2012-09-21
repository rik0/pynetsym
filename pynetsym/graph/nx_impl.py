from  . import interface
import networkx as nx
from traits.api import HasTraits, Instance
from traits.api import DelegatesTo
from traits.has_traits import implements
from ._abstract import AbstractGraph


class NxGraph(AbstractGraph):
    implements(interface.IGraph)


    nx_graph = Instance(nx.Graph, allow_none=False)

    number_of_nodes = DelegatesTo('nx_graph')
    number_of_edges = DelegatesTo('nx_graph')



    def __init__(self, graph_type=nx.Graph, data=None, **kwargs):
        self.nx_graph = graph_type(data=data, **kwargs)

    def add_node(self):
        self.nx_graph.add_node(self.index_store.take())

    def add_edge(self, source, target):
        self.nx_graph.add_edge(source, target)

    def remove_edge(self, source, target):
        self.nx_graph.remove_edge(source, target)

