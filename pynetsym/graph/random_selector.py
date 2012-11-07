from traits.api import Interface
from traits.api import HasTraits, implements
from traits.api import false

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

    _initialized_preferential_attachment = false

    def preferential_attachment(self):
        if not self._initialized_preferential_attachment:
            self.prepare_preferential_attachment()
            self._initialized_preferential_attachment = True
        return self.extract_preferential_attachment()

    def prepare_preferential_attachment(self):
        raise NotImplementedError()

    def random_edge(self):
        raise NotImplementedError()

    def random_node(self):
        raise NotImplementedError()

    def extract_preferential_attachment(self):
        raise NotImplementedError()