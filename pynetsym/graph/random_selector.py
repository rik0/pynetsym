import random
import numpy as np
from traits.api import Interface
from traits.api import HasTraits, implements
from traits.api import false
from traits.trait_numeric import Array
from traits.trait_types import Instance
from pynetsym.graph import IGraph

class IRandomSelector(Interface):
    def random_node(self):
        """
        Return a random node
        @return: a random node
        @rtype: int
        """
        pass

    def random_edge(self):
        """
        Return a random edge
        @return: a random edge
        @rtype: (int, int)
        """
        pass

    def preferential_attachment(self):
        """
        Return a node according to preferential attachment.
        @return: a random node
        @rtype: int
        """
        pass

    def prepare_preferential_attachment(self):
        """
        If preferential_attachment has never been required, the necessary structures
         are not initialized. This method creates them. The structures are transparently
         created when preferential-attachment is required for the first time, however,
         it is possible to explicitly require the re-initialization.
        """


class AbstractRandomSelector(HasTraits):
    implements(IRandomSelector)

    graph_container = Instance(IGraph)
    _initialized_preferential_attachment = false

    def preferential_attachment(self):
        if not self._initialized_preferential_attachment:
            self.prepare_preferential_attachment()
            self._initialized_preferential_attachment = True
        return int(self.extract_preferential_attachment())

    def prepare_preferential_attachment(self):
        raise NotImplementedError()

    def random_edge(self):
        raise NotImplementedError()

    def random_node(self):
        raise NotImplementedError()

    def extract_preferential_attachment(self):
        raise NotImplementedError()

class RepeatedNodesRandomSelector(AbstractRandomSelector):

    repeated_nodes = Array(dtype=np.int32, shape=(None, ))

    def extract_preferential_attachment(self):
        return random.choice(self.repeated_nodes)

    def add_edge(self, source, target):
        if self._initialized_preferential_attachment:
            # this is embarassingly inefficient! Fix somehow!
            self.repeated_nodes = np.append(self.repeated_nodes, [source, target])

    def remove_edge(self, source, target):
        if self._initialized_preferential_attachment:
            self.repeated_nodes.sort()
            # algorithm supposes source and target are in the array!
            source_index = self.repeated_nodes.searchsorted(source)
            target_index = self.repeated_nodes.searchsorted(target)
            min_index = min(source_index, target_index)
            max_index = max(source_index, target_index)
            self.repeated_nodes = np.hstack(
                [self.repeated_nodes[:min_index],
                 self.repeated_nodes[min_index + 1:max_index],
                 self.repeated_nodes[max_index + 1:]])

    def remove_node(self, node):
        self._initialized_preferential_attachment = False
        self.repeated_nodes = np.zeros(0, dtype=np.int32)

    def add_node(self, node):
        if self._initialized_preferential_attachment:
            self.repeated_nodes = np.append(self.repeated_nodes, node)
