import random
import networkx
from traits.trait_types import Enum, Int, Float, Set, Instance
from pynetsym import Simulation, Node, Activator, Agent
from pynetsym.configurators import NXGraphConfigurator
from pynetsym.simulation import BaseClock


class Recorder(Agent):
    name = 'recorder'
    current_time = Int(0)

    def setup(self):
        self.send(BaseClock.name,
                  'register_observer', name=self.name)

    def ticked(self):
        self.current_time += 1

    def node_infected(self):
        pass

    def node_recovered(self):
        pass


class Activator(Activator):
    infected_nodes = Set(Int)

    def infected(self, node):
        self.infected_nodes.add(node)
        self.send(Recorder.name, 'node_infected')

    def not_infected(self, node):
        self.infected_nodes.remove(node)
        self.send(Recorder.name, 'node_recovered')

    def nodes_to_activate(self):
        return self.infected_nodes


class Specimen(Node):
    state = Enum('S', 'I', 'R')
    infection_time = Int(-1)
    infection_probability = Float
    infection_length = Int
    infected_fraction = Float

    def initialize(self):
        if random.random() < self.infected_fraction:
            self.infect()

    def infect(self):
        if self.state == 'S':
            self.state = 'I'
            self.infection_time = self.infection_length
            self.send(Activator.name, 'infected', node=self.id)

    def activate(self):
        if (self.state == 'I'
            and self.infection_time > 0):
            for node in self.neighbors():
                if random.random() < self.infection_time:
                    self.send(node, 'infect')
            self.infection_time -= 1
        elif (self.state == 'I'
              and self.infection_time == 0):
            self.infection_time -= 1
            self.state = 'R'
            self.send(Activator.name, 'not_infected', node=self.id)
        elif self.state in ('R', 'S'):
            pass
        else:
            self.send_log('I should not get here.')


class Simulation(Simulation):
    default_infection_probability = 0.01
    default_infection_length = 10
    default_infected_fraction = 0.005

    steps = 1000

    additional_agents = (
        (Recorder, (), {}),
    )

    command_line_options = (
        ('-p', '--infection-probability',
            dict(default=default_infection_probability, type=float)),
        ('-t', '--infection-length',
            dict(default=default_infection_length, type=int)),
        ('-f', '--infected-fraction',
            dict(default=default_infected_fraction, type=float)),
    )

    activator_type = Activator
    activator_options = {}

    class configurator_type(NXGraphConfigurator):
        node_cls = Specimen
        node_options = {'infection_probability', 'infection_length', 'infected_fraction'}
        initialize_nodes = True


if __name__ == '__main__':
    graph = networkx.powerlaw_cluster_graph(100, 5, 0.1)
    sim = Simulation()
    sim.run(starting_graph=graph)
