from pynetsym.storage.basic import GraphError, GraphWrapper
import itertools as it
import pynetsym.rndutil
import random
import types

try:
    import networkx as nx
except ImportError, nx_import_exception:
    nx = types.ModuleType('networkx', 'Fake module')

    class NXGraphWrapper(GraphWrapper):
        def __init__(self):
            raise nx_import_exception
else:
    class NXGraphWrapper(GraphWrapper):
        def __init__(self):
            self.graph = nx.Graph()
            self.repeated_nodes = []

        @property
        def handle(self):
            return self.graph

        def random_nodes(self, how_many):
            sample = random.sample(self.nodes())
            return [node.id for node in sample]

        def random_node(self):
            """
            Draw a random node from the graph.

            @return: a node index
            @rtype: int
            @raise GraphError if the graph is empty.

            @warning: notice that it assumes that the graph nodes have
                indices going from 0 to some n. If it is not the case,
                the draw may not be uniform, bugs may arise, demons may
                fly out of your node.
            """
            ## TODO: this is wrong from a probabilistic point of view
            ## Fix it using additional data structures and for example
            ## a layer of indirection
            ## mapping each index with a single node
            try:
                max_value = self.graph.number_of_nodes()
                chosen_index = random.randrange(0, max_value)
            except ValueError:
                raise GraphError("Extracting node from empty graph.")
            else:
                if self.graph.has_node(chosen_index):
                    return chosen_index
                else:
                    logging.warning("The network is not filled.")
                    return pynetsym.rndutil.choice_from_iter(
                        self.graph.nodes_iter(),
                        max_value)

        def preferential_attachment_node(self):
            """
            Return a random node chosen according to pref. attachment

            @return: a node
            @rtype: int
            """
            try:
                return random.choice(self.repeated_nodes)
            except IndexError:
                raise GraphError("Extracting node from empty graph.")

        def add_edge(self, source, target):
            self.graph.add_edge(source, target)
            self.repeated_nodes.append(source)
            self.repeated_nodes.append(target)

        def remove_edge(self, source, target):
            self.graph.remove_edge(source, target)
            self.repeated_nodes.remove(source)
            self.repeated_nodes.remove(target)

        def random_edge(self):
            """
            Draw a random edge from the graph.

            @return: a pair of nodes representing an edge
            @rtype: (int, int)
            @raise GraphError: if the graph has no edges.

            @warning: this is relatively safe, although horribly slow.
            """
            try:
                return pynetsym.rndutil.choice_from_iter(
                    self.graph.edges_iter(),
                    self.graph.number_of_edges())
            except ValueError:
                raise GraphError(
                        "Extracting edge from graph with no edges")

        def add_node(self, identifier, agent):
            self.graph.add_node(identifier, agent=agent)
            assert identifier == agent.id
            self.repeated_nodes.append(identifier)

        def remove_node(self, identifier):
            self.graph.remove_node(identifier)
            self.repeated_nodes.remove(identifier)

        def __contains__(self, identifier):
            return identifier in self.graph

        def __getitem__(self, identifier):
            try:
                return self.graph.node[identifier]['agent']
            except (IndexError, KeyError):
                raise GraphError("Cannot find node %s." % identifier)

        def neighbors(self, node_identifier):
            return self.graph.neighbors(node_identifier)

        def nodes(self):
            nodes_with_data = self.graph.nodes_iter(data=True)
            return nodes_with_data
