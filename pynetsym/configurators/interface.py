from traits.api import Interface
from traits.api import Method

class IConfigurator(Interface):
    def create_nodes(self):
        pass

    def create_edges(self):
        pass

    initialize_nodes = Method
