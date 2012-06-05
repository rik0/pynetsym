from pynetsym import node_manager
from pynetsym import argutils

import networkx as nx


class StartingNXGraphConfigurator(node_manager.Configurator):
    # starting_graph

    configurator_options = {'starting_graph'}

    def setup(self):
        self.node_arguments = argutils.extract_options(
                self.additional_arguments, self.node_options)
        node_manager_id = node_manager.NodeManager.name
        graph = self.starting_graph
        assert isinstance(graph, nx.Graph)

        self.node_map = {}
        # create all the nodes
        for node in graph.nodes_iter():
            answ = self.send(node_manager_id, 'create_node',
                       cls=self.node_cls, parameters=self.node_arguments)
            identifier = answ.get()
            self.node_map[node] = identifier
        for u, v in graph.edges_iter():
            u1 = self.node_map[u]
            v1 = self.node_map[v]
            self.send(v1, 'accept_link', originating_node=u1)
        self.initialize_nodes()
        self.kill()

