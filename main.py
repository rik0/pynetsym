import sys

import argparse

import networkx as nx

from os import path
from pynetsym.address_book import  AddressBook
from pynetsym.core import uniform_spawn_strategy, NodeManager
from pynetsym.generation import  make_activator
from pynetsym.models import transitive_linking
from pynetsym import timing

CHOICES = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')

def save_network(network, out, fmt):
    if out is None and fmt is None:
        return
    elif out is None:
        out = 'network'
    elif fmt is None:
        out, ext = path.splitext(out)
        fmt = ext[1:]
        if fmt not in CHOICES:
            print "Error"
            return
    fn = getattr(nx, 'write_' + fmt)
    fn(network, out + '.' + fmt)


def main(steps, activate_function, network_size, p):
    graph = nx.Graph()
    address_book = AddressBook()
    node_manager = NodeManager(graph, address_book,
        transitive_linking.make_setup(
            network_size,
            death_probability=p))
    node_manager.start()

    activator = make_activator(
        steps, activate_function,
        graph, address_book)
    activator.join()
    node_manager.join()
    return graph

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Synthetic Network Generation Utility')
    parser.add_argument('-s', '--steps', default=100, type=int)
    parser.add_argument('-n', '--nodes', default=100, type=int)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-f', '--format', choices=CHOICES,
        default=None)
    namespace = parser.parse_args(sys.argv[1:])

    with timing.Timer(timing.Timer.execution_printer(sys.stdout)):
        network = main(
            steps=namespace.steps,
            activate_function=transitive_linking.activate,
            network_size=namespace.nodes,
            p=0.1)
    save_network(network, namespace.output, namespace.format)
