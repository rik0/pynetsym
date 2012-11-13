from pynetsym.generation_models import nx_barabasi_albert as ba
from pynetsym.graph import ScipyGraph


class SBA(ba.BA):
    graph_type = ScipyGraph

    @property
    def graph_options(self):
        graph_size = self.steps + self.starting_network_size + 1
        return dict(max_nodes=graph_size)

if __name__ == '__main__':
    sim = SBA()
    sim.run()
