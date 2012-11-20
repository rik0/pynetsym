import itertools
import traceback
from numpy import savetxt, dtype, zeros, array, zeros_like
import os
from os import path
import time
import networkx as nx
from plfit import plfit

import csv

from pynetsym import AsyncClock, BasicConfigurator
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert


Node = barabasi_albert.Node
Activator = barabasi_albert.Activator

BA_SyncClock = barabasi_albert.BA

class InterruptingNode(Node):
    def activate(self):
        forbidden = set()
        forbidden.add(self.id)
        while self.starting_edges:
            random_node = self.graph.random_selector.preferential_attachment()
            if random_node not in forbidden:
                self.link_to(random_node)
                forbidden.add(random_node)
                self.starting_edges -= 1
            self.cooperate()


class InterruptingNodeActivator(Activator):
    def nodes_to_create(self):
        return [(InterruptingNode, dict(starting_edges=self.starting_edges))]


BA_UninterruptibleHandler_SyncClock = barabasi_albert.BA

class BA_UninterruptibleHandler_AsyncClock(barabasi_albert.BA):
    clock_type = AsyncClock

    @property
    def clock_options(self):
        return dict(remaining_ticks=self.steps)


class BA_InterruptingNode_SyncClock(barabasi_albert.BA):
    activator_type = InterruptingNodeActivator

    class configurator_type(BasicConfigurator):
        node_type = InterruptingNode
        node_options = {'starting_edges'}


class BA_InterruptingNode_AsyncClock(barabasi_albert.BA):
    clock_type = AsyncClock
    activator_type = InterruptingNodeActivator

    @property
    def clock_options(self):
        return dict(remaining_ticks=self.steps)

    class configurator_type(BasicConfigurator):
        node_type = InterruptingNode
        node_options = {'starting_edges'}


# starting_edges=11, starting_network_size=11, steps=100000
def run_simulation(sim_class, **kwargs):
    sim = sim_class()
    sim.setup_parameters(**kwargs)
    sim.run(**kwargs)

    with sim.graph.handle as graph:
        return graph


def base_file(base, **kwargs):
    kwargs['base'] = base
    return ('%(base)s_%(type)s_'
            '%(starting_edges)d_'
            '%(starting_network_size)d_'
            '%(steps)d.%(fmt)s') % kwargs


def log(what, **kwargs):
    print ('%(type)s_'
           '%(starting_edges)d_'
           '%(starting_network_size)d_'
           '%(steps)d:') % kwargs,
    try:
        print what % kwargs['args']
    except KeyError:
        print what


def full_path(filename):
    return path.join(DIRECTORY_NAME, filename)


def save_graph_info(graph, **kwargs):
    nx.write_graphml(
        graph, full_path(
            base_file('graph', fmt='graphml', **kwargs)))
    degrees = graph.degree().values()
    savetxt(full_path(
        base_file('degrees', fmt='csv', **kwargs)),
            degrees, fmt='%i')
    return degrees


def fit(degrees, **kwargs):
    gamma, xmin, L = plfit(degrees)
    log('(gamma=%(gamma)s, xmin=%(xmin)s, L=%(L)s)',
        args=locals(), **kwargs)
    return gamma, xmin, L

DIRECTORY_NAME = "%s_%d" % (
    path.splitext(__file__)[0],
    time.time())

os.mkdir(DIRECTORY_NAME)
types_of_simulation = dict(BAUHSC=BA_UninterruptibleHandler_SyncClock,
                           BAUHAC=BA_UninterruptibleHandler_AsyncClock,
                           BAIHSC=BA_InterruptingNode_SyncClock,
                           BAIHAC=BA_InterruptingNode_AsyncClock)

default_starting_edges = 11
default_starting_network_size = 11

record_type = dtype(([('steps', int)] +
                     [('%s_%s' % (type, field), float)
                      for type in types_of_simulation.keys()
                      for field in ['gamma', 'xmin', 'L']]))
names = array(record_type.names)

all_steps = [2000, 5000, 10000, 15000]
# all_steps = [100, 200]

data = zeros((len(all_steps), ), dtype=record_type)

for row, steps in enumerate(all_steps):
    data[row]['steps'] = steps
    start = 1
    for type in types_of_simulation:
        try:
            args = dict(type=type,
                        starting_edges=default_starting_edges,
                        starting_network_size=default_starting_network_size,
                        steps=steps)
            graph = run_simulation(types_of_simulation[type], **args)
            degrees = save_graph_info(graph, **args)
            gamma, xmin, L = fit(degrees, **args)
            current_names = names[start:start + 3]
            for name, val in zip(current_names, [gamma, xmin, L]):
                data[row][name] = val
            del graph
            del degrees
        except Exception as e:
            traceback.print_last()
        finally:
            start += 3

savetxt(full_path('fits.csv'), data, delimiter=', ')