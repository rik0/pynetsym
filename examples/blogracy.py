

from scipy import stats
from pynetsym import core, configurators, simulation
from pynetsym import geventutil


class State(object):
    def __init__(self, node):
        self.node = node
        
class OfflineState(object):
    pass

class OnlineState(object):
    pass

class Node(core.Node):
    def generate(self):
        self.state = self.awake_state
        self.state.generate()
        
    def update(self):
        self.state = self.awake_state
        self.state.update()


class Activator(simulation.Activator):
    activator_options = {'generation_probability', 'update_probability'}
    
    def setup(self):
        number_of_nodes = self.graph.number_of_nodes()
        self.generation_variate = stats.binom(
            number_of_nodes, self.generation_probability)
        self.update_variate = stats.binom(
            number_of_nodes, self.update_probability)        
    
    def tick(self):
        # todo... check what we have to do when stuff is awake or not
        self.generation_stage()
        self.update_state()
        
    def generation_stage(self):
        number_of_nodes = self.generation_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        self.send_all(nodes, 'generate')
        
    def update_stage(self):
        number_of_nodes = self.update_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        self.send_all(nodes, 'update')

class Simulation(simulation.Simulation):
    
    command_line_options = (
        ('--generation-probability', dict(type=probability, default=0.05)),
        ('--update-probability', dict(type=probability, default=0.05)),
    )
    
    class configurator_type(configurators.StartingNXGraphConfigurator):
        node_cls = Node
        node_options = {}
        