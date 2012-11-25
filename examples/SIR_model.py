import random
import math
import networkx
from traits.trait_types import Enum, Int, Float, Set

from pynetsym import Simulation
from pynetsym import Node
from pynetsym import Activator
from pynetsym import Agent

from pynetsym.simulation import BaseClock
from pynetsym.configurators import NXGraphConfigurator
from pynetsym.termination.conditions import always_true

import pandas as pd
import numpy as np
from pynetsym.util import SequenceAsyncResult

def nans(shape, dtype=float):
    a = np.empty(shape, dtype)
    a.fill(np.nan)
    return a

class Recorder(Agent):
    name = 'recorder'
    current_time = Int(0)

    def setup(self):
        self.distributions = pd.DataFrame(
            data=nans((self.steps, 2)),
            columns=['infected', 'recovered'])
        self.distributions.ix[self.current_time] = 0
        self.send(BaseClock.name,
                  'register_observer', name=self.name)

    def ticked(self):
        self.current_time += 1
        self.distributions.ix[self.current_time] =\
        self.distributions.ix[self.current_time - 1]


    def node_infected(self, node):
        self.send_log('[%d] infected %s' % (
            self.current_time, node))
        self.distributions.infected[self.current_time] += 1

    def node_recovered(self, node):
        self.send_log('[%d] recovered %s' % (
            self.current_time, node))
        self.distributions.infected[self.current_time] -= 1
        self.distributions.recovered[self.current_time] += 1


class Activator(Activator):
    infected_nodes = Set(Int)

    def tick(self):
        if self.infected_nodes:
            super(Activator, self).tick()
        else:
            self.signal_termination('No more infected')

    def infected(self, node):
        self.infected_nodes.add(node)
        self.send(Recorder.name, 'node_infected', node=node)

    def not_infected(self, node):
        self.infected_nodes.remove(node)
        self.send(Recorder.name, 'node_recovered', node=node)

    def nodes_to_activate(self):
        return self.infected_nodes


class Specimen(Node):
    state =  Enum('S', 'I', 'R')
    remaining_infection_time = Int(-1)
    infection_probability = Float
    infection_length = Int
    infected_fraction = Float

    # DEBUG_SEND = True

    def infection_time(self):
        return self.infection_length

    def initialize(self, state):
        self.state = state
        if state == 'I':
            self.remaining_infection_time = self.infection_time()
            self.send(Activator.name, 'infected', node=self.id)

    def infect(self):
        if self.state == 'S':
            self.state = 'I'
            self.remaining_infection_time = self.infection_time()
            self.send(Activator.name, 'infected', node=self.id)

    def activate(self):
        if (self.state == 'I'
            and self.remaining_infection_time > 0):
            for node in self.neighbors():
                if random.random() < self.infection_probability:
                    self.send(node, 'infect')
            self.remaining_infection_time -= 1
        elif (self.state == 'I'
              and self.remaining_infection_time == 0):
            self.remaining_infection_time -= 1
            self.state = 'R'
            self.send(Activator.name, 'not_infected', node=self.id)
        elif self.state in ('R', 'S'):
            pass
        else:
            self.send_log('I should not get here.')


class Simulation(Simulation):
    default_infection_probability = 1.
    default_infection_length = 10
    default_infected_fraction = 0.01

    steps = 1000

    recorder_type = Recorder
    recorder_options = {'steps'}

    additional_agents = ('recorder', )

    class termination_checker_type(Simulation.termination_checker_type):
        def require_termination(self, reason):
            self.add_condition(always_true(reason))

    command_line_options = (
        ('-p', '--infection-probability',
         dict(default=default_infection_probability, type=float)),
        ('-t', '--infection-length',
         dict(default=default_infection_length, type=int)),
        ('-f', '--infected-fraction',
         dict(default=default_infected_fraction, type=float)),
        )

    activator_type = Activator
    options = {}

    class configurator_type(NXGraphConfigurator):
        node_type = Specimen
        node_options = {
            'infection_probability',
            'infection_length',
            'infected_fraction'}

        def initialize_nodes(self):
            infected_fraction = self.full_parameters['infected_fraction']
            infected_population_size = int(
                math.ceil(len(self.node_identifiers) * infected_fraction))
            infected_nodes = set(random.sample(self.node_identifiers, infected_population_size))

            self.sync_send_all(self.node_identifiers, 'initialize',
                          state=lambda rid: 'I' if (rid in infected_nodes) else 'S')



if __name__ == '__main__':
    graph = networkx.powerlaw_cluster_graph(100, 5, 0.1)
    sim = Simulation()
    sim.run(starting_graph=graph)

    assert sim.motive == 'No more infected'

    network_size = sim.graph.number_of_nodes()
    df = sim.recorder.distributions.dropna()

    full_df = pd.concat(
        [df, pd.DataFrame(data=-(df.infected + df.recovered) + network_size,
                          columns=['susceptible'])],
        axis=1)
    assert isinstance(full_df, pd.DataFrame)
    print full_df.describe()

    full_df.to_csv('SIR_model.csv', index_label='step')