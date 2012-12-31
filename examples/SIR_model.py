import math
import random
from traits.trait_types import Enum, CInt, Float, Set, Instance

import gevent
from pynetsym import Simulation
from pynetsym import Agent

import pynetsym

from pynetsym.configurators import BasicH5Configurator

from pynetsym.termination.conditions import always_true
from pynetsym.graph import BasicH5Graph
from pynetsym.agent_db import MongoAgentDB

from pymongo import MongoClient

class Clock(pynetsym.Clock):
    options = {'steps', 'mongo_client', 'graph'}

    def clock_loop(self):
        susceptible = self.graph.number_of_nodes()

        self.mongo_client.drop_database('stats')
        self.db = self.mongo_client.stats
        self.distributions = self.db.distributions

        self.distributions.insert({
            'current_time': self.current_time,
            'susceptible': susceptible,
            'infected': 0,
            'recovered': 0
        })

        while (self.active and
               self.current_time < self.steps):
            self.sync_send_tick()
            self.distribution.insert(
                    self.distributions.find_one({
                        'current_time': self.current_time}).update(
                            current_time=self.current_time+1))
            self.current_time += 1
        else:
            self.simulation_end()


class Activator(pynetsym.Activator):
    infected_nodes = Set(CInt)

    def tick(self, time):
        if self.infected_nodes:
            super(Activator, self).tick(time)
        else:
            self.signal_termination('No more infected')

    def infected(self, node, time):
        self.infected_nodes.add(node)

    def not_infected(self, node, time):
        self.infected_nodes.remove(node)

    def nodes_to_activate(self, time):
        return self.infected_nodes


class Node(pynetsym.Node):
    state = Enum('S', 'I', 'R')
    recovery_rate = Float(1.0)
    infection_rate = Float(1.0)

    mongo_client = Instance(MongoClient, transient=True)

    infected_fraction = Float

    def setup_mongo(self):
        self._db = self.mongo_client.stats
        self._distributions = self._db.distributions
        self._stats = self._db.infections

    def mark_infected(self, time):
        self._distributions.update(
                {'current_time': time},
                {'$inc': {'infected': 1, 'susceptible': -1}})
        self._stats.insert({
            'node': int(self.id),
            'start': time,
            'end': None,
            })

    def mark_recovered(self, time):
        self._distributions.update(
                {'current_time': time},
                {'$inc': {'infected': -1, 'recovered': 1}})
        self._stats.update(
                {'node': int(self.id)},
                {'$set': {'end': time}})

    def initialize(self, state):
        self.state = state
        if state == 'I':
            self.send(Activator.name, 'infected',
                    node=self.id, time=0)
            self.mark_infected(0)

    def infect(self, time):
        self.mongo_client
        if self.state == 'S':
            self.state = 'I'
            self.send(Activator.name, 'infected', node=self.id,
                    time=time)
            self.mark_infected(time)

    def activate(self, time):
        if self.state == 'I':
            for node in self.neighbors():
                if random.random() < self.infection_rate:
                    self.send(node, 'infect', time=time)
            if random.random() < self.recovery_rate:
                self.state = 'R'
                self.send(Activator.name, 'not_infected', node=self.id,
                        time=time)
                self.mark_recovered(time)
        elif self.state in ('R', 'S'):
            pass
        else:
            self.send_log('I should not get here.')


class Simulation(pynetsym.Simulation):
    default_infection_rate = 1.
    default_recovery_rate = 1.
    default_infected_fraction = 0.01

    mongo_client = MongoClient()

    agent_db_type = MongoAgentDB
    agent_db_parameters = {'mongo_client': mongo_client}

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
            'initial_infected_fraction',
            'mongo_client'}

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
