import math
import random
import networkx
from numpy import arange
from traits.trait_types import Enum, Int, Float, Set

from pynetsym import Simulation
from pynetsym import Node
from pynetsym import Activator
from pynetsym import Agent

from pynetsym.simulation import BaseClock, Activator
from pynetsym.configurators import NXGraphConfigurator
from pynetsym.termination.conditions import always_true

import pandas as pd
import numpy as np

def nans(shape, dtype=float):
    a = np.empty(shape, dtype)
    a.fill(np.nan)
    return a


class Recorder(Agent):
    name = 'recorder'
    current_time = Int(-1)

    def setup(self):
        self.number_of_nodes = 1000
        self.distributions = pd.DataFrame(
            data=nans((self.steps + 1, 3)),
            columns=['susceptible', 'infected', 'recovered'],
            index=arange(-1, self.steps))
        self.distributions.ix[self.current_time] = 0
        self.distributions.susceptible.ix[self.current_time] = self.number_of_nodes
        self.send(BaseClock.name,
                  'register_observer', name=self.name)

    def ticked(self):
        self.current_time += 1
        self.distributions.ix[self.current_time] =\
        self.distributions.ix[self.current_time - 1]


    def node_infected(self, node):
        self.distributions.infected[self.current_time] += 1
        self.distributions.susceptible[self.current_time] -= 1

    def node_recovered(self, node):
        self.distributions.infected[self.current_time] -= 1
        self.distributions.recovered[self.current_time] += 1

    def _save_infected_ratio(self):
        df = self.distributions.dropna()
        df.to_csv('SIR_model.csv', index_label='step')

    def save_statistic(self):
        self._save_infected_ratio()


class AdvancedRecorder(Recorder):
    def setup(self):
        super(AdvancedRecorder, self).setup()

        self.infection_times = pd.DataFrame(
            data=nans((self.number_of_nodes, 2)),
            columns=['infection', 'recovery'])

    def node_infected(self, node):
        super(AdvancedRecorder, self).node_infected(node)
        self.infection_times.infection[node] = self.current_time

    def node_recovered(self, node):
        super(AdvancedRecorder, self).node_recovered(node)
        self.infection_times.recovery[node] = self.current_time

    def _save_infection_times(self):
        df = self.infection_times.dropna()
        df['duration'] = (df.recovery - df.infection)
        df.to_csv('SIR_model_infection_rates.csv', index_label='node')

    def save_statistic(self):
        super(AdvancedRecorder, self).save_statistic()
        self._save_infection_times()


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
    state = Enum('S', 'I', 'R')
    recovery_rate = Float(1.0)
    infection_rate = Float(1.0)

    infected_fraction = Float

    # DEBUG_SEND = True

    def initialize(self, state):
        self.state = state
        if state == 'I':
            self.send(Activator.name, 'infected', node=self.id)

    def infect(self):
        if self.state == 'S':
            self.state = 'I'
            self.send(Activator.name, 'infected', node=self.id)

    def activate(self):
        if self.state == 'I':
            for node in self.neighbors():
                if random.random() < self.infection_rate:
                    self.send(node, 'infect')
            if random.random() < self.recovery_rate:
                self.state = 'R'
                self.send(Activator.name, 'not_infected', node=self.id)
        elif self.state in ('R', 'S'):
            pass
        else:
            self.send_log('I should not get here.')


class Simulation(Simulation):
    default_infection_rate = 1.
    default_recovery_rate = 1.
    default_infected_fraction = 0.01

    recorder_type = AdvancedRecorder
    recorder_options = {'steps'}

    additional_agents = ('recorder', )

    class termination_checker_type(Simulation.termination_checker_type):
        def require_termination(self, reason):
            self.add_condition(always_true(reason))

    command_line_options = (
        ('-p', '--infection-rate',
         dict(default=default_infection_rate, type=float)),
        ('-r', '--recovery-rate',
         dict(default=default_recovery_rate, type=float)),
        ('-f', '--initial-infected-fraction',
         dict(default=default_infected_fraction, type=float)),
        )

    activator_type = Activator
    options = {}

    class configurator_type(NXGraphConfigurator):
        node_type = Specimen
        node_options = {
            'infection_rate',
            'recovery_rate',
            'initial_infected_fraction'}

        def initialize_nodes(self):
            infected_fraction = self.full_parameters['initial_infected_fraction']
            infected_population_size = int(
                math.ceil(len(self.node_identifiers) * infected_fraction))
            infected_nodes = set(random.sample(self.node_identifiers, infected_population_size))
            self.sync_send_all(self.node_identifiers, 'initialize',
                               state=lambda rid: 'I' if (rid in infected_nodes) else 'S')


if __name__ == '__main__':
    graph = networkx.powerlaw_cluster_graph(1000, 50, 0.2)
    sim = Simulation()
    sim.run(starting_graph=graph, force_cli=True)

    print sim.motive

    network_size = sim.graph.number_of_nodes()
    sim.recorder.save_statistic()
