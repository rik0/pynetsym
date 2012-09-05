from traits.trait_types import Instance, Class
from pynetsym import argutils
from pynetsym import node_manager
from pynetsym import geventutil

import itertools
import networkx as nx
from pynetsym.storage import GraphWrapper


class StartingNXGraphConfigurator(node_manager.Configurator):
    configurator_options = {'starting_graph'}

    starting_graph = Instance(GraphWrapper)
    node_cls = Class
    node_options = Instance(set)

    def create_edges(self):
        graph = self.starting_graph
        for u, v in graph.edges_iter():
            u1 = self.node_map[u]
            v1 = self.node_map[v]
            self.send(v1, 'accept_link', originating_node=u1)

    def create_nodes(self):
        self.node_arguments = argutils.extract_options(
                self.additional_arguments, self.node_options)
        node_manager_id = node_manager.NodeManager.name
        graph = self.starting_graph
        assert isinstance(graph, nx.Graph)

        self.node_map = {}
        # create all the nodes
        nit_1, nit_2 = itertools.tee(graph.nodes_iter())
        answers = [self.send(node_manager_id, 'create_node',
                       cls=self.node_cls, parameters=self.node_arguments)
                       for _node in nit_1]
        self.node_map = {node: identifier for node, identifier
            in itertools.izip(nit_2,
                geventutil.SequenceAsyncResult(answers).get())}
        self.node_identifiers = self.node_map.viewvalues()

