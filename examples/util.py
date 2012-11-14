import collections
import numpy as np
from numpy import ndarray, fromiter
from pynetsym.util import sna
import networkx as nx

__author__ = 'enrico'

def make_distributions(arg):
    if isinstance(arg, nx.Graph):
        values = arg.degree().values()
    elif isinstance(arg, collections.Sequence):
        values = arg
    elif isinstance(arg, ndarray):
        values = arg.flatten()
    else:
        raise TypeError("Don't know what to do with %s" % arg)

    bins = np.bincount(values)
    ccdf = sna.ccdf(bins)
    pdf = np.asfarray(bins) / np.sum(bins)
    return ccdf, pdf