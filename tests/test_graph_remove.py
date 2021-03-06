import paramunittest
import networkx
from pynetsym.graph import ScipyGraph, NxGraph

@paramunittest.parametrized(
    (ScipyGraph, lambda: dict(max_nodes=12, )),
    (NxGraph, lambda: dict(graph=networkx.Graph())),
    (NxGraph, lambda: dict(graph=networkx.DiGraph()))
)
class TestGraphRemoveNode(paramunittest.ParametrizedTestCase):
    def setParameters(self, factory, make_parameters):
        self.factory = factory
        self.make_parameters = make_parameters

    def setUp(self):
        self.number_of_initial_nodes = 5
        self.graph = self.factory(**self.make_parameters())
        self.graph.add_nodes(self.number_of_initial_nodes)
        for target in xrange(1, self.number_of_initial_nodes):
            self.graph.add_edge(0, target)

    def testRemoveNotExisting(self):
        self.assertRaises(ValueError, self.graph.remove_node, self.number_of_initial_nodes)

    def testRemoveLeafNode(self):
        number_of_edges = self.graph.number_of_edges()
        self.graph.remove_node(self.number_of_initial_nodes-1)
        self.assertEquals(self.number_of_initial_nodes-1, self.graph.number_of_nodes())
        self.assertEquals(number_of_edges-1, self.graph.number_of_edges())

    def testRemoveStarCenter(self):
        self.graph.remove_node(0)
        self.assertEquals(self.number_of_initial_nodes-1, self.graph.number_of_nodes())
        self.assertEquals(0, self.graph.number_of_edges())
