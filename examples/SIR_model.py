import math
import random
from traits.trait_types import Enum, Int, CInt, Float, Set

import gevent
from pynetsym import Simulation
from pynetsym import Activator
from pynetsym import Agent

import pynetsym

from pynetsym.simulation import BaseClock
from pynetsym.configurators import BasicH5Configurator
from pynetsym.termination.conditions import always_true
from pynetsym.graph import BasicH5Graph
from pynetsym.agent_db import MongoAgentDB

from pymongo import MongoClient

class Recorder(Agent):
    name = 'recorder'
    current_time = Int(-1)

    options = {'steps', 'graph', }

    def setup(self):
        self.number_of_nodes = self.graph.number_of_nodes()
        self.susceptible = self.number_of_nodes
        self.infected = 0
        self.recovered = 0

        self.client = MongoClient()
        self.client.drop_database('stats')
        self.db = self.client.stats
        self.distributions = self.db.distributions

        self.send(BaseClock.name,
                  'register_observer', name=self.name)

    def ticked(self):
        self.distributions.insert({
            'current_time': self.current_time,
            'susceptible': self.susceptible,
            'infected': self.infected,
            'recovered': self.recovered})
        self.current_time += 1

    def node_infected(self, node):
        self.susceptible -= 1
        self.infected += 1

    def node_recovered(self, node):
        self.infected -= 1
        self.recovered += 1


class AdvancedRecorder(Recorder):
    def setup(self):
        super(AdvancedRecorder, self).setup()
        self.infections = self.db.infections

    def node_infected(self, node):
        super(AdvancedRecorder, self).node_infected(node)
        self.infections.insert(dict(
            node=int(node),
            start=self.current_time,
            end=None))

    def node_recovered(self, node):
        super(AdvancedRecorder, self).node_recovered(node)
        self.infections.update(
                dict(node=int(node)),
                {'$set': dict(end=self.current_time)})

class Activator(pynetsym.Activator):
    infected_nodes = Set(CInt)

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


class Node(pynetsym.Node):
    state = Enum('S', 'I', 'R')
    recovery_rate = Float(1.0)
    infection_rate = Float(1.0)

    infected_fraction = Float

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


class Simulation(pynetsym.Simulation):
    default_infection_rate = 1.
    default_recovery_rate = 1.
    default_infected_fraction = 0.01

    agent_db_type = MongoAgentDB
    agent_db_parameters = {}


    recorder_type = AdvancedRecorder

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
        ('--h5-file', dict(default='', type=str)),
        )

    activator_type = Activator
    activator_options = {}

    graph_type = BasicH5Graph
    graph_options = {'h5_file', }

    class configurator_type(BasicH5Configurator):
        node_type = Node
        node_options = {
            'infection_rate',
            'recovery_rate',
            'initial_infected_fraction'}

        def initialize_nodes(self):
            infected_fraction = self.full_parameters[
                    'initial_infected_fraction']
            infected_population_size = int(
                math.ceil(
                    len(self.node_identifiers) * infected_fraction))
            infected_nodes = set(
                    random.sample(
                        self.node_identifiers,
                        infected_population_size))
            self.sync_send_all(
                   self.node_identifiers, 'initialize',
                   state=lambda rid: ('I' if (rid in infected_nodes)
                                            else 'S'))

def bench_mem(timeout, filename='meliae-dump-'):
    try:
        from meliae import scanner
        import time
    except ImportError:
        pass
    else:
        gevent.sleep(timeout)
        scanner.dump_all_objects(
                '%s%d.json' % (filename, time.clock()))

if __name__ == '__main__':
    sim = Simulation()

    # gevent.spawn(bench_mem, 15.0)
    sim.run(force_cli=True)

    print sim.motive

    network_size = sim.graph.number_of_nodes()
    # sim.recorder.save_statistic()
