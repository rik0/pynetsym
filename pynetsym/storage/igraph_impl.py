import random
import types
from pynetsym.storage.basic import GraphError, GraphWrapper

try:
    import igraph
except ImportError, igraph_import_exception:
    igraph = types.ModuleType('igraph', 'Fake module')

    class IGraphWrapper(GraphWrapper):
        def __init__(self):
            raise igraph_import_exception
else:
    class IGraphWrapper(GraphWrapper):
        def __init__(self, graph):
            """
            Creates an implementation of Graph backed with igraph.Graph
            @param graph: the backing graph
            @type graph: igraph.Graph
            """
            self.graph = graph
            self.repeated_nodes = []

        def add_node(self, identifier, agent):
            self.graph.add_vertices(1)
            largest_index = len(self.graph.vs) - 1
            self.graph.vs[largest_index]["identifier"] = identifier
            self.graph.vs[largest_index]["agent"] = agent
            self.repeated_nodes.append(identifier)

        def __getitem__(self, identifier):
            return self.graph.vs[identifier]["agent"]

        def add_edge(self, source, target):
            self.graph.add_edges(((source, target), ))
            self.repeated_nodes.append(source)
            self.repeated_nodes.append(target)

        def remove_edge(self, source, target):
            self.graph.delete_edges(((source, target), ))
            self.repeated_nodes.remove(source)
            self.repeated_nodes.remove(target)

        def random_nodes(self, how_many):
            """
            Return a sample of how_many nodes.
            """
            return random.sample(how_many, range(0, len(self.graph.vs)))


        def random_node(self):
            try:
                return random.randrange(0, len(self.graph.vs))
            except IndexError:
                raise GraphError("Extracting node from empty graph.")

        def random_edge(self):
            try:
                edge = random.choice(self.graph.es)
                return edge.source, edge.target
            except IndexError:
                raise GraphError(
                        "Extracting edge from graph with no edges")

        def preferential_attachment_node(self):
            try:
                return random.choice(self.repeated_nodes)
            except IndexError:
                raise GraphError("Extracting node from empty graph.")

        def remove_node(self, identifier):
            raise NotImplementedError()

        @property
        def handle(self):
            return self.graph

        def __contains__(self, identifier):
            if 0 < identifier < len(self.graph.vs):
                return True
            else:
                return False

        def neighbors(self, node_identifier):
            return self.graph.neighbors(node_identifier)

        def nodes(self):
            indices = self.graph.vs.indices
            for index in indices:
                yield index, self.graph.vs[index].attributes()
