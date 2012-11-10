__all__ = [
    'Either',
    'IConfigurator',
    'AbstractConfigurator',
    'BasicConfigurator'
]



from .predicates import Either
from .interface import IConfigurator
from .basic import AbstractConfigurator, BasicConfigurator

try:
    import networkx
    del networkx
except ImportError:
    pass
else:
    from nx_configurator import NXGraphConfigurator
    __all__.append('NXGraphConfigurator')


