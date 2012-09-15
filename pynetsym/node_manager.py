from gevent.pool import Group
from traits.trait_types import   Instance

from pynetsym import core

from pynetsym.identifiers_manager import IntIdentifierStore

class NodeManager(core.Agent):
    """
    The class responsible to create nodes.

    """
    name = 'manager'

    id_store = Instance(IntIdentifierStore, allow_none=False, args=())

    """
    the registered name in the L{address book<AddressBook>}
    """

    def __init__(self, graph):
        """
        Creates a new node_manager

        @param graph: the graph to pass to the agents
        @type graph: storage.GraphWrapper
        """
        self.graph = graph
        self.failures = []
        self.group = Group()

    # TODO: deal with returning identifiers.

    def fill_node(self, node):
        self.graph.add_node(node.id)
        node._greenlet.link_value(node._remove_from_network)
        node.graph = self.graph
        self.group.add(node._greenlet)

    def create_node(self, cls, parameters):
        """
        Creates a new node.

        @param cls: the factory creating the new node.
            Usually the node class.
        @type cls: callable
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        @return: the actual identifier
        @rtype: int | str
        """
        node = cls(**parameters)
        identifier = self.id_store.pop()
        node.start(self._address_book, self._node_db, identifier)
        return identifier

    def simulation_ended(self):
        message = 'SIMULATION ENDED: REMAINING %d NODES.' % len(self.group)
        self.send_log(message)
        self.group.join()


