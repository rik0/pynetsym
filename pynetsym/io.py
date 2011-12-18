import networkx as nx
from os import path

FORMATS = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')

def save_network(network, network_path=None, fmt=None, **kwargs):
    if network_path is None and fmt is None:
        return
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
    if fmt is None:
        _, ext = path.splitext(network_path)
        fmt = ext[1:]
        if fmt not in FORMATS:
            raise IOError("Did not undestand format from filename %s." % network_path)
    fn = getattr(nx, 'read_' + fmt)
    fn(network_path, **kwargs)