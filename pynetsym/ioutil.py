"""
This modules contains functions related to IO.

These functions have been written to be easy to use from interactive prompt
and such more than to be general. Lot of DIP has B{not} been done on purpose.
"""

import networkx as nx
from os import path

FORMATS = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')
"""Available formats"""

def save_network(network, network_path=None, fmt=None, **kwargs):
    """
    Saves the specified network to the file network_path
    @param network: the network to save
    @type network: networkx.Graph
    @param network_path: the file path. If it is not specified and the
        format is specified, assumes the value is network.format
    @param fmt: the format to save the network into. Chose among
        L{FORMATS}
    @param kwargs: additional arguments to be passed to the underlying
        networkx.write_* function
    @raise ValueError: if both network_path and fmt are none or if
        the specified format is not supported.
    @raise IOError: if the inferred format is not valid.
    """
    if network_path is None and fmt is None:
        raise ValueError("Either specify the filename or the format.")
    elif network_path is None:
        network_path = 'network'
    elif fmt is None:
        network_path, ext = path.splitext(network_path)
        fmt = ext[1:]
        if fmt not in FORMATS:
            raise IOError("Did not undestand format from filename %s." % network_path)
    try:
        fn = getattr(nx, 'write_' + fmt)
    except AttributeError:
        raise ValueError("Could not save in %s format." % fnt)
    fn(network, network_path + '.' + fmt, **kwargs)

def read_network(network_path, fmt=None, **kwargs):
    """
    Reads a network from filesystem.
    @param network_path: The file to read the network from
    @param fmt: the format the network was stored in (some kind of guessing is
        made from the filename, if left blank)
    @param kwargs: Additional arguments to be passed to the corresponding
        networkx.read_* function
    @return: the network
    @rtype: networkx.Graph
    """
    if fmt is None:
        _, ext = path.splitext(network_path)
        fmt = ext[1:]
        if fmt not in FORMATS:
            raise IOError("Did not undestand format from filename %s." % network_path)
    fn = getattr(nx, 'read_' + fmt)
    return fn(network_path, **kwargs)

def distribution_to_csv(distribution, fileobj, **kwargs):
    """
    Saves a distribution to file as a csv
    @param distribution: the distribution to save
    @type distribution: ((a, ...))
    @param fileobj: a file like object to save stuff into
    @type fileobj: file
    @param kwargs: additional parameters to be passed to the csv.writer
    """
    import csv

    csv_writer = csv.writer(fileobj, **kwargs)
    for row in distribution:
        csv_writer.writerow(row)


