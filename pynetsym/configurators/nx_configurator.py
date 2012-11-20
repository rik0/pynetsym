from traits.trait_types import Instance, Class, Type
from pynetsym import node_manager


import itertools
import networkx as nx

from pynetsym.util import extract_subdictionary, SequenceAsyncResult
from .basic import AbstractConfigurator

class NXGraphConfigurator(AbstractConfigurator):
    options = {'starting_graph'}

    starting_graph = Instance(nx.Graph, allow_none=False)

    node_type = Type
    node_options = Instance(set)

    def create_edges(self):
        graph = self.starting_graph
        for u, v in graph.edges_iter():
            u1 = self.node_map[u]
            v1 = self.node_map[v]
            self.send(v1, 'accept_link', originating_node=u1)

    def create_nodes(self):
        self.node_arguments = extract_subdictionary(
                self.full_parameters, self.node_options)
        node_manager_id = node_manager.NodeManager.name
        graph = self.starting_graph
        assert isinstance(graph, nx.Graph)

        self.node_map = {}
        # create all the nodes
        nit_1, nit_2 = itertools.tee(graph.nodes_iter())
        answers = [self.send(node_manager_id, 'create_node',
                       cls=self.node_type, parameters=self.node_arguments)
                       for _node in nit_1]
        self.node_map = {node: identifier for node, identifier
            in itertools.izip(nit_2,
                SequenceAsyncResult(answers).get())}
        self.node_identifiers = self.node_map.viewvalues()

