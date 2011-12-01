#!/usr/bin/env python

import sys

import argparse

import networkx as nx

from os import path
from pynetsym import timing, plugins, core, generation

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


def base_parser():
    parser = argparse.ArgumentParser(
        add_help=False,
        description='Synthetic Network Generation Utility')
    parser.add_argument('-s', '--steps', default=100, type=int)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-f', '--format', choices=CHOICES, default=None)
    return parser


def parse_arguments(default_module):
    parent_parser = base_parser()
    try:
        module_name = sys.argv[1]
    except IndexError:
        module_name = default_module
    module = plugins.load_plugin(module_name)
    parser = module.make_parser(parent=parent_parser)
    namespace = parser.parse_args(sys.argv[2:])
    arguments_dictionary = vars(namespace)
    return arguments_dictionary, module


def main():
    arguments_dictionary, module = parse_arguments(default_module='transitive_linking')
    output = arguments_dictionary.pop('output')
    format = arguments_dictionary.pop('format')
    steps = arguments_dictionary.pop('steps')

    graph = nx.Graph()

    with timing.Timer(timing.execution_printer(sys.stdout)):
        address_book = core.AddressBook()
        node_manager = core.NodeManager(graph, address_book,
            module.make_setup(**arguments_dictionary))
        node_manager.start()

        activator = generation.Activator(graph, address_book)
        activator.start()

        clock = generation.Clock(steps, address_book)
        clock.start()

        activator.join()
        node_manager.join()
    save_network(graph, output, format)


if __name__ == '__main__':
    main()
