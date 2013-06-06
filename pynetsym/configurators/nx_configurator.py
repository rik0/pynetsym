from traits.trait_types import Instance, Class, Type
from pynetsym import node_manager


import itertools
import networkx as nx

from pynetsym.util import extract_sub_dictionary, SequenceAsyncResult
from .basic import AbstractConfigurator


class NXGraphConfigurator(AbstractConfigurator):
    """
    Sets up a network reading the initial configuration from a graph
    in a file supported by the NetworkX library.
    """

    options = {'starting_graph'}
    """
    The NXGraphConfigurator agent reads the `starting_graph` property
    """

    starting_graph = Instance(nx.Graph, allow_none=False)

    node_type = Type
    node_options = Instance(set)

    def create_edges(self):
        """
        Creates the edges as specified in the network it read.
        """
        graph = self.starting_graph
        for u, v in graph.edges_iter():
            u1 = self.node_map[u]
            v1 = self.node_map[v]
            self.send(v1, 'accept_link', originating_node=u1)

    def create_nodes(self):
        """
        Requires the `NodeManager` to create the nodes as specified in the network it read.
        """
        self.node_arguments = extract_sub_dictionary(
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

