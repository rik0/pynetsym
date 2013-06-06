"""
Barabasi-Albert Model with Scipy backend.

Barabasi AL, Albert R (1999) Emergence of scaling in random networks. Science 286:509-51

Here we reuse the definition of the Node and of the
activator from the nx_barabasi_implementation.

We simply change the graph backend, so we only override
some parameters in the Simulation class.
"""

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
