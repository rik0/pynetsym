from networkx.generators.classic import empty_graph
from networkx.generators.random_graphs import _random_subset
from pynetsym import core
from pynetsym import node_manager
from pynetsym import simulation
import networkx as nx
import operator
import random



class ba_stepper(object):
    def __init__(self, graph, n, m, seed=None):
        self.graph = graph
        if m < 1 or  m >= n:
            raise nx.NetworkXError(\
                  ("Barabasi-Albert network must "
                      "have m>=1 and m<n, m=%d,n=%d") % (m, n))
        self.n = n
        self.m = m
        self.graph.name = "barabasi_albert_graph(%s,%s)" % (n, m)
        if seed is not None:
            self.seed = random.seed(seed)
        else:
            self.seed = seed

    def __iter__(self):
        # node creation should have provided these.
        assert self.graph.handle.number_of_nodes() > self.m
        # Target nodes for new edges
        targets = map(operator.itemgetter(0), self.graph.nodes())
        # List of existing nodes, with nodes repeated once for each adjacent edge
        repeated_nodes = []
        # Start adding the other n-m nodes. The first node is m.
        source = self.m
        while source < self.n:
            # Add edges to m nodes from the source.
            # G.add_edges_from(zip([source] * m, targets))
            # Add one node to the list for each new edge just created.
            repeated_nodes.extend(targets)
            # And the new node "source" has m edges to add to the list.
            repeated_nodes.extend([source] * self.m)
            yield targets
            # Now choose m unique nodes from the existing nodes
            # Pick uniformly from repeated_nodes (preferential attachement)
            targets = _random_subset(repeated_nodes, self. m)
            source += 1


class Node(core.Node):
    def __init__(self, identifier, address_book, graph, stepper):
        super(Node, self).__init__(identifier, address_book, graph)
        self.stepper = stepper

    def activate(self):
        try:
            candidates = next(self.stepper)
        except StopIteration:
            graph = self.graph.handle
            print graph.number_of_edges(),
            print graph.number_of_nodes(),
            print self.id
        else:
            for candidate in candidates:
                self.link_to(candidate)


class Activator(simulation.Activator):
    activator_options = {'stepper'}

    def nodes_to_activate(self):
        return self.fresh_nodes

    def nodes_to_create(self):
        return [(Node, dict(stepper=self.stepper))]


class BA(simulation.Simulation):
    default_starting_edges = 5
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_edges, type=int)),
        ('-m', '--starting-edges',
            dict(default=default_starting_edges, type=int)),
        ('--seed', dict(default=None, type=int)))

    activator_type = Activator

    class configurator_type(node_manager.SingleNodeConfigurator):
        node_cls = Node
        node_options = {'stepper'}

    def set_up(self):
        total_network_size = self.starting_network_size + self.steps
        stepper = ba_stepper(
            self.graph,
            total_network_size, self.starting_edges, self.seed)
        self.add_parameter('stepper', iter(stepper))

if __name__ == '__main__':
    sim = BA()
    sim.run()

