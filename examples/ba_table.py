import itertools

import plfit

import networkx as nx
import numpy as np

from pynetsym.generation_models import nx_barabasi_albert as ba

from pynetsym import timing

import gc

#DIMENSIONS = [1000, 5000, 10000, 50000]
#DIMENSIONS = [10, 50, 100, 500]
DIMENSIONS = [5000]
#INITIAL_EDGES = [5, 8, 11, 20]
#INITIAL_EDGES = [5, 8]
INITIAL_EDGES = [5, ]
from pynetsym.util import approximate_cpl


lines = []

t = timing.Timer()
t.tic()
for n, m in itertools.product(DIMENSIONS, INITIAL_EDGES):
    sim = ba.BA()
    sim.callback = lambda *_: None
    sim.run(starting_network_size=m, starting_edges=m, steps=n-m)
    
    print 'Run simulation BA({}{})'.format(n, m)
    sim_graph = sim.graph.handle
    del sim
    sim_C = nx.average_clustering(sim_graph)
    print '\tComputed clustering'
    sim_CPL = approximate_cpl(sim_graph)
    print '\tComputed CPL'
    sim_alpha, sim_xmin, sim_L = plfit.plfit(sim_graph.degree().values())
    print '\tComputed Alpha'
    del sim_graph
    gc.collect()
    print '\tCollected'
    
    nx_graph = nx.barabasi_albert_graph(n, m)
    print 'Created BA({},{})'.format(n, m)
    nx_C = nx.average_clustering(nx_graph)
    print '\tComputed clustering'
    nx_CPL = approximate_cpl(nx_graph)
    print '\tComputed CPL'
    nx_alpha, nx_xmin, nx_L = plfit.plfit(nx_graph.degree().values())
    print '\tComputed Alpha'
    del nx_graph
    gc.collect()
    print '\tCollected' 
    
    an_C = n ** (-0.75)    
    an_CPL = np.log(n)/np.log(np.log(n))
            
    lines.append(("%(n)s & %(m)s & "
                  "%(sim_C)1.2e & %(sim_CPL)1.2g & %(sim_alpha)1.2g & "
                  "%(nx_C)1.2e & %(nx_CPL)1.2g & %(nx_alpha)1.2g & "
                  "%(an_C)1.2e & %(an_CPL)1.2g \\\\") % locals())
        
t.toc()
print 'Elapsed:', t.elapsed_time
print 
print
print '\n'.join(lines)

    
    