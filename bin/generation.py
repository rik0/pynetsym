#!/usr/bin/env python

import sys

import argparse

import networkx as nx

from pynetsym import plugins, generation, io

def base_parser():
    parser = argparse.ArgumentParser(
        add_help=False,
        description='Synthetic Network Generation Utility')
    parser.add_argument('-s', '--steps', default=100, type=int)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('-f', '--format', choices=io.FORMATS, default=None)
    return parser


def parse_arguments(args, default_module):
    parent_parser = base_parser()
    try:
        module_name = args[0]
    except IndexError:
        module_name = default_module
    module = plugins.load_plugin(module_name)
    parser = module.make_parser(parent=parent_parser)
    namespace = parser.parse_args(args[1:])
    arguments_dictionary = vars(namespace)
    return arguments_dictionary, module


def main(args):
    arguments_dictionary, module = parse_arguments(args, default_module='transitive_linking')
    output_path = arguments_dictionary.pop('output')
    format = arguments_dictionary.pop('format')
    steps = arguments_dictionary.pop('steps')

    graph = nx.Graph()

    generation.generate(graph, module, steps, arguments_dictionary)
    io.save_network(graph, output_path, format)


if __name__ == '__main__':
    main(sys.argv[1:])
