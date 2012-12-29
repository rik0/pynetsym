from traits.trait_types import Instance, Class, Type
from pynetsym import node_manager

import itertools
import networkx as nx

import h5py

from pynetsym.util import extract_subdictionary, SequenceAsyncResult
from .basic import AbstractConfigurator

class BasicH5Configurator(AbstractConfigurator):
    options = {'h5_file'}

    starting_graph = Instance(h5py.File, allow_none=False)

    node_type = Type
    node_options = Instance(set)

    def create_edges(self):
        pass

    def create_nodes(self):
        ifile = h5py.File(self.h5_file, 'r')
        indptr = ifile['indptr']
        max_node = indptr.len() - 1
        
        self.node_arguments = extract_subdictionary(
                self.full_parameters, self.node_options)
        node_manager_id = node_manager.NodeManager.name

        answers = [self.send(node_manager_id, 'create_node',
                       cls=self.node_type, parameters=self.node_arguments)
                       for _ in xrange(max_node)]
        SequenceAsyncResult(answers).get()
        self.node_identifiers = xrange(max_node)


    