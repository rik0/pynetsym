import random
import networkx as nx

from pynetsym import core
from pynetsym import simulation
from pynetsym import node_manager

class Node(core.Node):
    #DEBUG_SEND = True
    #DEBUG_RECEIVE = True

    def __init__(self, identifier, address_book, graph, starting_network_size):
        super(Node, self).__init__(identifier, address_book, graph)
        self.starting_network_size = starting_network_size
        self.all_nodes = range(self.starting_network_size)
        self.activated = False

    def activate(self):
        if not self.activated:
            for node, _attrs in self.graph.nodes():
                if node != self.id:
                    self.link_to(node)
            self.activated = True
        else:
            candidates = self.graph.neighbors(self.id)
            dropped = random.sample(
                candidates,
                random.randrange(1 if len(candidates) else 0, len(candidates)))
            for node in dropped:
                self.unlink_from(node)



class Activator(simulation.Activator):
    #DEBUG_SEND = True
    #DEBUG_RECEIVE = True

    activator_options = {'starting_network_size'}

    def setup(self):
        self.next_node = 0

    def nodes_to_activate(self):
        node = self.next_node
        cycle = node / self.starting_network_size
        self.next_node += 1

        if cycle == 0:
            return [node]
        elif cycle == 1:
            return []
        elif cycle == 2:
            return [node % self.starting_network_size]
        else:
            return []



class Sim(simulation.Simulation):
    default_starting_nodes = 20
    command_line_options = (
        ('-n', '--starting-network-size',
            dict(default=default_starting_nodes, type=int)),
    )

    activator_type = Activator

    class configurator_type(node_manager.BasicConfigurator):
        node_cls = Node
        node_options = {'starting_network_size'}


if __name__ == '__main__':
    sim = Sim()
    graph = sim.graph.handle
    assert isinstance(graph, nx.Graph)

    #nx.draw(graph)
    #plt.show()

    sim.run()

    print nx.is_isomorphic(
        nx.complete_graph(len(graph)),
        graph)

    #nx.draw(graph)
    #plt.show()

    import gc
    all_objects = gc.get_objects()
    all_nodes = filter(lambda o: isinstance(o, Node), all_objects)
    del all_objects

    import objgraph



    objgraph.show_backrefs(all_nodes, filename='refs.png')
#
#    print len(all_nodes)
#    for index in range(len(all_nodes)):
#        if all_nodes[index].ready():
#            print all_nodes[index]
#            referrers = gc.get_referrers(all_nodes[index])
#            referrers.remove(all_nodes)
#
#            for referrer in referrers:
#                print '\t', referrer
#                for key, value in referrer.iteritems():
#                    if value is all_nodes[index]:
#                        print '\t\t', key
#                    super_referrers = gc.get_referrers(referrer)
#                    for sref in super_referrers:
#                        print '\t\t\t', type(sref)
#
#
#            del referrers
#            del referrer
