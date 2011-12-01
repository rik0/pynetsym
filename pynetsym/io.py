import networkx as nx

FORMATS = ('dot', 'gexf', 'gml', 'gpickle',
           'graphml', 'pajek', 'yaml')

def save_network(network, out, fmt):
    if out is None and fmt is None:
        return
    elif out is None:
        out = 'network'
    elif fmt is None:
        out, ext = path.splitext(out)
        fmt = ext[1:]
        if fmt not in FORMATS:
            print "Error"
            return
    fn = getattr(nx, 'write_' + fmt)
    fn(network, out + '.' + fmt)