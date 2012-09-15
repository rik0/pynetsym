import greenlet
import random
import gevent
import networkx as nx

import traits.api as t

from pynetsym import simulation, BasicConfigurator
from pynetsym import node_manager
from pynetsym.nodes import Node

import sys

#sys.stderr =x open('/dev/null', 'w')

class Node(Node):
    DEBUG_SENT = True
    DEBUG_RECEIVED = True

    _activated = t.false

    def activate(self):
        if not self._activated:
            for node, _attrs in self.graph.nodes():
                if node != self.id:
                    self.link_to(node)
            self._activated = True
        else:
            candidates = self.graph.neighbors(self.id)
            dropped = random.sample(
                candidates,
                random.randrange(1 if len(candidates) else 0, len(candidates)))
            for node in dropped:
                self.unlink_from(node)
            if random.random() < 0.1:
                raise gevent.GreenletExit()



class Activator(simulation.Activator):

    DEBUG_SENT = True
    DEBUG_RECEIVED = True

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

    class configurator_type(BasicConfigurator):
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

    print graph.nodes()
    print graph.number_of_edges()

    print sim.id_manager.get_identifier()

    #nx.draw(graph)
    #plt.show()


#    objgraph.show_backrefs(all_nodes, filename='refs.png')
