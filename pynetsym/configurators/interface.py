from traits.has_traits import Interface

class IConfigurator(Interface):
    def create_nodes(self):
        pass

    def create_edges(self):
        pass

    def do_initialize_nodes(self):
        pass

    @property
    def initialize_node(self):
        pass
