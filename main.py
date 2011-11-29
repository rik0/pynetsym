import sys

import argparse

import networkx as nx

from os import path
from pynetsym.address_book import  AddressBook
from pynetsym.core import uniform_spawn_strategy, NodeManager
from pynetsym.generation import  make_activator
from pynetsym.models.transitive_linking import TLNode, tl_activate
from pynetsym.timing import Timer


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

def main(steps, activate_function, spawn_strategy, nodes_number, p):
    graph = nx.Graph()
    address_book = AddressBook()
    node_manager = NodeManager(spawn_strategy, graph,
                                address_book,
                                network_size=nodes_number,
                                death_probability=p)
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

    with Timer(Timer.execution_printer(sys.stdout)):
        network = main(
            steps=namespace.steps,
            activate_function=tl_activate,
            spawn_strategy=uniform_spawn_strategy(TLNode),
            nodes_number=namespace.nodes,
            p=0.1)
    save_network(network, namespace.output, namespace.format)
